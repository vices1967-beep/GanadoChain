from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg, Sum
from django.conf import settings
from .metrics_models import SystemMetrics
from .serializers import (
    SystemMetricsSerializer,
    SystemMetricsSummarySerializer,
    HealthCheckSerializer,
    SystemConfigSerializer,
    DashboardStatsSerializer,
    ValidationTestSerializer,
    ErrorResponseSerializer,
    SuccessResponseSerializer,
    PaginationSerializer
)
import logging
import psutil
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SystemMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para métricas del sistema"""
    serializer_class = SystemMetricsSerializer
    permission_classes = [permissions.IsAdminUser]  # Solo administradores
    
    def get_queryset(self):
        queryset = SystemMetrics.objects.all()
        
        # Filtros
        days = self.request.query_params.get('days', None)
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        
        if days:
            from_date = timezone.now().date() - timedelta(days=int(days))
            queryset = queryset.filter(date__gte=from_date)
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
            
        return queryset.order_by('-date')
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Obtener la métrica más reciente"""
        latest_metric = SystemMetrics.objects.order_by('-date').first()
        if not latest_metric:
            return Response({
                'success': False,
                'error': 'No hay métricas disponibles'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(latest_metric)
        return Response({
            'success': True,
            'metric': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Resumen de métricas del sistema"""
        days = int(request.query_params.get('days', 30))
        from_date = timezone.now().date() - timedelta(days=days)
        
        metrics = SystemMetrics.objects.filter(date__gte=from_date)
        
        if not metrics.exists():
            return Response({
                'success': False,
                'error': f'No hay métricas para los últimos {days} días'
            }, status=status.HTTP_404_NOT_FOUND)
        
        summary = {
            'date_range': f'{from_date} to {timezone.now().date()}',
            'total_animals': metrics.aggregate(Sum('total_animals'))['total_animals__sum'] or 0,
            'total_users': metrics.aggregate(Sum('total_users'))['total_users__sum'] or 0,
            'total_transactions': metrics.aggregate(Sum('total_transactions'))['total_transactions__sum'] or 0,
            'active_devices': metrics.aggregate(Avg('active_devices'))['active_devices__avg'] or 0,
            'average_gas_price': metrics.aggregate(Avg('average_gas_price'))['average_gas_price__avg'] or 0,
            'blockchain_events': metrics.aggregate(Sum('blockchain_events'))['blockchain_events__sum'] or 0,
            'health_alerts': metrics.aggregate(Sum('health_alerts'))['health_alerts__sum'] or 0,
            'producer_count': metrics.aggregate(Sum('producer_count'))['producer_count__sum'] or 0,
            'vet_count': metrics.aggregate(Sum('vet_count'))['vet_count__sum'] or 0,
            'frigorifico_count': metrics.aggregate(Sum('frigorifico_count'))['frigorifico_count__sum'] or 0,
            'auditor_count': metrics.aggregate(Sum('auditor_count'))['auditor_count__sum'] or 0,
            'avg_response_time': metrics.aggregate(Avg('avg_response_time'))['avg_response_time__avg'] or 0,
            'error_rate': metrics.aggregate(Avg('error_rate'))['error_rate__avg'] or 0,
            'system_uptime': metrics.aggregate(Avg('system_uptime'))['system_uptime__avg'] or 0
        }
        
        serializer = SystemMetricsSummarySerializer(summary)
        return Response({
            'success': True,
            'summary': serializer.data
        })

class HealthCheckView(APIView):
    """Vista para health check del sistema"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        # Verificar base de datos
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            database_status = True
        except Exception as e:
            database_status = False
            logger.error(f"Database health check failed: {str(e)}")
        
        # Verificar blockchain (conexión básica)
        try:
            from web3 import Web3
            from web3.exceptions import ConnectionError
            w3 = Web3(Web3.HTTPProvider(settings.BLOCKCHAIN_RPC_URL))
            blockchain_status = w3.is_connected()
        except (ConnectionError, Exception) as e:
            blockchain_status = False
            logger.error(f"Blockchain health check failed: {str(e)}")
        
        # Verificar dispositivos IoT (conexión básica)
        try:
            iot_status = True  # Placeholder - implementar verificación real
        except Exception as e:
            iot_status = False
            logger.error(f"IoT health check failed: {str(e)}")
        
        # Métricas del sistema
        memory = psutil.virtual_memory()
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # Obtener uptime del sistema
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                uptime = timedelta(seconds=uptime_seconds)
        except:
            uptime = timedelta(seconds=0)
        
        health_data = {
            'status': 'healthy' if all([database_status, blockchain_status, iot_status]) else 'degraded',
            'timestamp': timezone.now(),
            'database': database_status,
            'blockchain': blockchain_status,
            'iot_devices': iot_status,
            'version': settings.VERSION if hasattr(settings, 'VERSION') else '1.0.0',
            'uptime': uptime,
            'memory_usage': memory.percent,
            'cpu_usage': cpu_usage,
            'disk_usage': psutil.disk_usage('/').percent,
            'active_connections': len(psutil.net_connections())
        }
        
        serializer = HealthCheckSerializer(health_data)
        return Response(serializer.data)

class SystemConfigView(APIView):
    """Vista para obtener configuración del sistema"""
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        config_data = {
            'blockchain_rpc_url': settings.BLOCKCHAIN_RPC_URL,
            'blockchain_chain_id': getattr(settings, 'BLOCKCHAIN_CHAIN_ID', 80002),
            'ipfs_gateway_url': getattr(settings, 'IPFS_GATEWAY_URL', 'https://ipfs.io/ipfs/'),
            'max_gas_price': getattr(settings, 'MAX_GAS_PRICE', 100000000000),
            'min_gas_price': getattr(settings, 'MIN_GAS_PRICE', 1000000000),
            'default_gas_limit': getattr(settings, 'DEFAULT_GAS_LIMIT', 21000),
            'transaction_timeout': getattr(settings, 'TRANSACTION_TIMEOUT', 120),
            'sync_interval': getattr(settings, 'SYNC_INTERVAL', 60),
            'health_check_interval': getattr(settings, 'HEALTH_CHECK_INTERVAL', 300),
            'max_retries': getattr(settings, 'MAX_RETRIES', 3),
            'debug': settings.DEBUG,
            'environment': getattr(settings, 'ENVIRONMENT', 'development')
        }
        
        serializer = SystemConfigSerializer(config_data)
        return Response(serializer.data)

class DashboardStatsView(APIView):
    """Vista para estadísticas del dashboard"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        from django.apps import apps
        
        # Importar modelos de otras apps
        Animal = apps.get_model('cattle', 'Animal')
        Batch = apps.get_model('cattle', 'Batch')
        IoTDevice = apps.get_model('iot', 'IoTDevice')
        User = apps.get_model('users', 'User')
        BlockchainEvent = apps.get_model('blockchain', 'BlockchainEvent')
        ContractInteraction = apps.get_model('blockchain', 'ContractInteraction')
        TransactionPool = apps.get_model('blockchain', 'TransactionPool')
        
        # Obtener estadísticas basadas en el rol del usuario
        if request.user.is_superuser:
            # Estadísticas globales para administradores
            stats = {
                'total_animals': Animal.objects.count(),
                'total_batches': Batch.objects.count(),
                'total_devices': IoTDevice.objects.count(),
                'total_users': User.objects.count(),
                
                'healthy_animals': Animal.objects.filter(health_status='HEALTHY').count(),
                'sick_animals': Animal.objects.filter(health_status='SICK').count(),
                'under_observation': Animal.objects.filter(health_status='UNDER_OBSERVATION').count(),
                
                'active_batches': Batch.objects.filter(status='CREATED').count(),
                'delivered_batches': Batch.objects.filter(status='DELIVERED').count(),
                'in_transit_batches': Batch.objects.filter(status='IN_TRANSIT').count(),
                
                'online_devices': IoTDevice.objects.filter(status='ACTIVE').count(),
                'offline_devices': IoTDevice.objects.filter(status='INACTIVE').count(),
                'low_battery_devices': IoTDevice.objects.filter(battery_level__lt=20).count(),
                
                'pending_transactions': TransactionPool.objects.filter(status='PENDING').count(),
                'confirmed_transactions': ContractInteraction.objects.filter(status='SUCCESS').count(),
                'failed_transactions': ContractInteraction.objects.filter(status='FAILED').count(),
                
                'current_gas_price': 0,  # Se obtendría del servicio de blockchain
                'avg_block_time': 2.1,  # Polygon Amoy
                'network_status': 'online'
            }
        else:
            # Estadísticas específicas del usuario
            stats = {
                'total_animals': Animal.objects.filter(owner=request.user).count(),
                'total_batches': Batch.objects.filter(created_by=request.user).count(),
                'total_devices': IoTDevice.objects.filter(owner=request.user).count(),
                
                'healthy_animals': Animal.objects.filter(owner=request.user, health_status='HEALTHY').count(),
                'sick_animals': Animal.objects.filter(owner=request.user, health_status='SICK').count(),
                'under_observation': Animal.objects.filter(owner=request.user, health_status='UNDER_OBSERVATION').count(),
                
                'active_batches': Batch.objects.filter(created_by=request.user, status='CREATED').count(),
                'delivered_batches': Batch.objects.filter(created_by=request.user, status='DELIVERED').count(),
                'in_transit_batches': Batch.objects.filter(created_by=request.user, status='IN_TRANSIT').count(),
                
                'online_devices': IoTDevice.objects.filter(owner=request.user, status='ACTIVE').count(),
                'offline_devices': IoTDevice.objects.filter(owner=request.user, status='INACTIVE').count(),
                'low_battery_devices': IoTDevice.objects.filter(owner=request.user, battery_level__lt=20).count(),
                
                'pending_transactions': 0,  # Placeholder
                'confirmed_transactions': 0,  # Placeholder
                'failed_transactions': 0,    # Placeholder
                
                'current_gas_price': 0,
                'avg_block_time': 2.1,
                'network_status': 'online'
            }
        
        # Intentar obtener gas price actual
        try:
            from web3 import Web3
            w3 = Web3(Web3.HTTPProvider(settings.BLOCKCHAIN_RPC_URL))
            stats['current_gas_price'] = w3.eth.gas_price
        except:
            pass
        
        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data)

class ValidationTestView(APIView):
    """Vista para probar validaciones"""
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        serializer = ValidationTestSerializer(data=request.data)
        
        if serializer.is_valid():
            return Response({
                'success': True,
                'message': 'Validaciones pasadas correctamente',
                'validated_data': serializer.validated_data
            })
        else:
            return Response({
                'success': False,
                'message': 'Errores de validación',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

class SystemMaintenanceView(APIView):
    """Vista para operaciones de mantenimiento del sistema"""
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        action = request.data.get('action')
        
        if action == 'clear_cache':
            try:
                from django.core.cache import cache
                cache.clear()
                return Response({
                    'success': True,
                    'message': 'Cache limpiado correctamente'
                })
            except Exception as e:
                return Response({
                    'success': False,
                    'error': f'Error limpiando cache: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        elif action == 'reindex_search':
            try:
                # Placeholder para reindexación de búsqueda
                return Response({
                    'success': True,
                    'message': 'Reindexación iniciada'
                })
            except Exception as e:
                return Response({
                    'success': False,
                    'error': f'Error en reindexación: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        elif action == 'update_metrics':
            try:
                from .tasks import update_system_metrics
                update_system_metrics.delay()
                return Response({
                    'success': True,
                    'message': 'Actualización de métricas iniciada'
                })
            except Exception as e:
                return Response({
                    'success': False,
                    'error': f'Error actualizando métricas: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        else:
            return Response({
                'success': False,
                'error': 'Acción no válida'
            }, status=status.HTTP_400_BAD_REQUEST)

class APIInfoView(APIView):
    """Vista para información de la API"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        info = {
            'api_name': 'GanadoChain API',
            'version': getattr(settings, 'API_VERSION', '1.0.0'),
            'environment': getattr(settings, 'ENVIRONMENT', 'development'),
            'documentation': f'{request.build_absolute_uri("/api/docs/")}',
            'supported_versions': ['v1'],
            'current_time': timezone.now(),
            'uptime': self.get_system_uptime(),
            'endpoints': {
                'animals': f'{request.build_absolute_uri("/api/cattle/animals/")}',
                'batches': f'{request.build_absolute_uri("/api/cattle/batches/")}',
                'devices': f'{request.build_absolute_uri("/api/iot/devices/")}',
                'users': f'{request.build_absolute_uri("/api/users/users/")}',
                'blockchain': f'{request.build_absolute_uri("/api/blockchain/events/")}'
            }
        }
        
        return Response(info)
    
    def get_system_uptime(self):
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                return str(timedelta(seconds=uptime_seconds))
        except:
            return "unknown"

class ErrorTestView(APIView):
    """Vista para probar manejo de errores"""
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        error_type = request.query_params.get('type', 'validation')
        
        if error_type == 'validation':
            return Response({
                'error': 'Validation Error',
                'code': 400,
                'message': 'Error de validación simulado',
                'details': {'field': ['Este campo es requerido']}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        elif error_type == 'not_found':
            return Response({
                'error': 'Not Found',
                'code': 404,
                'message': 'Recurso no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        elif error_type == 'server_error':
            return Response({
                'error': 'Server Error',
                'code': 500,
                'message': 'Error interno del servidor'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        elif error_type == 'permission':
            return Response({
                'error': 'Permission Denied',
                'code': 403,
                'message': 'No tienes permisos para esta acción'
            }, status=status.HTTP_403_FORBIDDEN)
        
        else:
            return Response({
                'error': 'Bad Request',
                'code': 400,
                'message': 'Tipo de error no válido'
            }, status=status.HTTP_400_BAD_REQUEST)