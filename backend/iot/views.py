from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg, Max, Min
from .models import IoTDevice, GPSData, HealthSensorData, DeviceEvent, DeviceConfiguration
from .serializers import (
    IoTDeviceSerializer, GPSDataSerializer, 
    HealthSensorDataSerializer, DeviceEventSerializer,
    DeviceConfigurationSerializer, IoTDataIngestSerializer,
    GPSDataIngestSerializer, HealthDataIngestSerializer,
    DeviceStatusUpdateSerializer, BulkDataIngestSerializer,
    DeviceRegistrationSerializer, AlertThresholdSerializer
)
from .permissions import IsDeviceOwner, IsIoTDevice
from cattle.models import Animal
import logging

logger = logging.getLogger(__name__)

class IoTDeviceViewSet(viewsets.ModelViewSet):
    serializer_class = IoTDeviceSerializer
    permission_classes = [permissions.IsAuthenticated, IsDeviceOwner]
    
    def get_queryset(self):
        queryset = IoTDevice.objects.filter(owner=self.request.user)
        
        # Filtros
        device_type = self.request.query_params.get('device_type', None)
        status = self.request.query_params.get('status', None)
        animal_id = self.request.query_params.get('animal_id', None)
        active = self.request.query_params.get('active', None)
        
        if device_type:
            queryset = queryset.filter(device_type=device_type)
        if status:
            queryset = queryset.filter(status=status)
        if animal_id:
            queryset = queryset.filter(animal_id=animal_id)
        if active == 'true':
            queryset = queryset.filter(status='ACTIVE')
        elif active == 'false':
            queryset = queryset.exclude(status='ACTIVE')
            
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Actualizar estado del dispositivo"""
        device = self.get_object()
        serializer = DeviceStatusUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            data = serializer.validated_data
            
            # Actualizar campos
            if 'status' in data:
                device.status = data['status']
            if 'battery_level' in data:
                device.battery_level = data['battery_level']
            if 'firmware_version' in data:
                device.firmware_version = data['firmware_version']
            if 'ip_address' in data:
                device.ip_address = data['ip_address']
            
            device.last_reading = timezone.now()
            device.save()
            
            # Crear evento si se proporciona mensaje
            if 'message' in data:
                DeviceEvent.objects.create(
                    device=device,
                    event_type='STATUS_UPDATE',
                    severity='LOW',
                    message=data['message'],
                    data={'status': device.status, 'battery_level': device.battery_level},
                    timestamp=timezone.now()
                )
            
            return Response({
                'success': True,
                'message': 'Estado del dispositivo actualizado',
                'device_id': device.device_id,
                'status': device.status
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def events(self, request, pk=None):
        """Obtener eventos del dispositivo"""
        device = self.get_object()
        events = device.events.all().order_by('-timestamp')
        serializer = DeviceEventSerializer(events, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Estadísticas del dispositivo"""
        device = self.get_object()
        
        stats = {
            'gps_data_count': device.gps_data.count(),
            'health_data_count': device.health_data.count(),
            'events_count': device.events.count(),
            'last_gps_data': device.gps_data.order_by('-timestamp').first(),
            'last_health_data': device.health_data.order_by('-timestamp').first(),
            'battery_level': device.battery_level,
            'status': device.status,
            'uptime': (timezone.now() - device.created_at).total_seconds() if device.created_at else 0
        }
        
        return Response(stats)

class GPSDataViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GPSDataSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = GPSData.objects.filter(animal__owner=self.request.user)
        
        # Filtros
        device_id = self.request.query_params.get('device_id', None)
        animal_id = self.request.query_params.get('animal_id', None)
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        accurate_only = self.request.query_params.get('accurate_only', None)
        
        if device_id:
            queryset = queryset.filter(device__device_id=device_id)
        if animal_id:
            queryset = queryset.filter(animal_id=animal_id)
        if date_from:
            queryset = queryset.filter(timestamp__gte=date_from)
        if date_to:
            queryset = queryset.filter(timestamp__lte=date_to)
        if accurate_only == 'true':
            queryset = queryset.filter(accuracy__lte=10.0)
            
        return queryset.order_by('-timestamp')
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Últimos datos GPS"""
        limit = int(request.query_params.get('limit', 10))
        data = self.get_queryset()[:limit]
        serializer = self.get_serializer(data, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def animal_track(self, request, animal_id):
        """Track completo de un animal"""
        animal = get_object_or_404(Animal, id=animal_id, owner=request.user)
        data = GPSData.objects.filter(animal=animal).order_by('timestamp')
        serializer = self.get_serializer(data, many=True)
        return Response(serializer.data)

class HealthSensorDataViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = HealthSensorDataSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = HealthSensorData.objects.filter(animal__owner=self.request.user)
        
        # Filtros
        device_id = self.request.query_params.get('device_id', None)
        animal_id = self.request.query_params.get('animal_id', None)
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        has_alerts = self.request.query_params.get('has_alerts', None)
        
        if device_id:
            queryset = queryset.filter(device__device_id=device_id)
        if animal_id:
            queryset = queryset.filter(animal_id=animal_id)
        if date_from:
            queryset = queryset.filter(timestamp__gte=date_from)
        if date_to:
            queryset = queryset.filter(timestamp__lte=date_to)
        if has_alerts == 'true':
            queryset = queryset.filter(health_alert=True)
            
        return queryset.order_by('-timestamp')
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Últimos datos de salud"""
        limit = int(request.query_params.get('limit', 10))
        data = self.get_queryset()[:limit]
        serializer = self.get_serializer(data, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def animal_health(self, request, animal_id):
        """Historial de salud de un animal"""
        animal = get_object_or_404(Animal, id=animal_id, owner=request.user)
        data = HealthSensorData.objects.filter(animal=animal).order_by('-timestamp')
        
        # Estadísticas
        stats = {
            'total_readings': data.count(),
            'avg_heart_rate': data.aggregate(avg=Avg('heart_rate'))['avg'],
            'avg_temperature': data.aggregate(avg=Avg('temperature'))['avg'],
            'alerts_count': data.filter(health_alert=True).count(),
            'last_reading': data.first().timestamp if data.exists() else None
        }
        
        serializer = self.get_serializer(data, many=True)
        return Response({
            'data': serializer.data,
            'stats': stats
        })

class DeviceEventViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DeviceEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = DeviceEvent.objects.filter(device__owner=self.request.user)
        
        # Filtros
        device_id = self.request.query_params.get('device_id', None)
        event_type = self.request.query_params.get('event_type', None)
        severity = self.request.query_params.get('severity', None)
        resolved = self.request.query_params.get('resolved', None)
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        
        if device_id:
            queryset = queryset.filter(device__device_id=device_id)
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        if severity:
            queryset = queryset.filter(severity=severity)
        if resolved == 'true':
            queryset = queryset.filter(resolved=True)
        elif resolved == 'false':
            queryset = queryset.filter(resolved=False)
        if date_from:
            queryset = queryset.filter(timestamp__gte=date_from)
        if date_to:
            queryset = queryset.filter(timestamp__lte=date_to)
            
        return queryset.order_by('-timestamp')

class IoTDataIngestView(APIView):
    permission_classes = [IsIoTDevice]
    
    def post(self, request):
        serializer = IoTDataIngestSerializer(data=request.data)
        if serializer.is_valid():
            device = request.device  # Set by IsIoTDevice permission
            processed_data = {'gps': 0, 'health': 0}
            
            # Procesar datos GPS
            if 'gps_data' in serializer.validated_data:
                gps_data = serializer.validated_data['gps_data']
                try:
                    animal = Animal.objects.get(ear_tag=gps_data['animal_ear_tag'])
                    
                    GPSData.objects.create(
                        device=device,
                        animal=animal,
                        latitude=gps_data['latitude'],
                        longitude=gps_data['longitude'],
                        altitude=gps_data.get('altitude'),
                        accuracy=gps_data.get('accuracy'),
                        speed=gps_data.get('speed'),
                        heading=gps_data.get('heading'),
                        satellites=gps_data.get('satellites'),
                        hdop=gps_data.get('hdop'),
                        timestamp=gps_data.get('timestamp', timezone.now())
                    )
                    processed_data['gps'] += 1
                    
                except Animal.DoesNotExist:
                    logger.warning(f"Animal con ear_tag {gps_data['animal_ear_tag']} no encontrado")
            
            # Procesar datos de salud
            if 'health_data' in serializer.validated_data:
                health_data = serializer.validated_data['health_data']
                try:
                    animal = Animal.objects.get(ear_tag=health_data['animal_ear_tag'])
                    
                    health_record = HealthSensorData.objects.create(
                        device=device,
                        animal=animal,
                        heart_rate=health_data.get('heart_rate'),
                        temperature=health_data.get('temperature'),
                        movement_activity=health_data.get('movement_activity'),
                        rumination_time=health_data.get('rumination_time'),
                        feeding_activity=health_data.get('feeding_activity'),
                        respiratory_rate=health_data.get('respiratory_rate'),
                        posture=health_data.get('posture'),
                        ambient_temperature=health_data.get('ambient_temperature'),
                        humidity=health_data.get('humidity'),
                        timestamp=health_data.get('timestamp', timezone.now())
                    )
                    
                    # Verificar alertas de salud
                    anomalies = health_record.has_anomalies
                    if anomalies:
                        health_record.health_alert = True
                        health_record.save()
                        
                        # Crear evento de alerta
                        DeviceEvent.objects.create(
                            device=device,
                            event_type='HEALTH_ALERT',
                            severity='HIGH',
                            message=f'Alerta de salud para {animal.ear_tag}: {", ".join(anomalies)}',
                            data={'animal_id': animal.id, 'anomalies': anomalies},
                            timestamp=timezone.now()
                        )
                    
                    processed_data['health'] += 1
                    
                except Animal.DoesNotExist:
                    logger.warning(f"Animal con ear_tag {health_data['animal_ear_tag']} no encontrado")
            
            # Actualizar último visto del dispositivo
            device.last_reading = timezone.now()
            device.save()
            
            return Response({
                'status': 'success',
                'processed': processed_data,
                'device_id': device.device_id,
                'timestamp': timezone.now()
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BulkDataIngestView(APIView):
    permission_classes = [IsIoTDevice]
    
    def post(self, request):
        serializer = BulkDataIngestSerializer(data=request.data)
        if serializer.is_valid():
            device = request.device
            processed_data = {'gps': 0, 'health': 0}
            
            # Procesar datos GPS en lote
            if 'gps_data' in serializer.validated_data:
                for gps_item in serializer.validated_data['gps_data']:
                    try:
                        animal = Animal.objects.get(ear_tag=gps_item['animal_ear_tag'])
                        GPSData.objects.create(
                            device=device,
                            animal=animal,
                            latitude=gps_item['latitude'],
                            longitude=gps_item['longitude'],
                            altitude=gps_item.get('altitude'),
                            accuracy=gps_item.get('accuracy'),
                            speed=gps_item.get('speed'),
                            timestamp=gps_item.get('timestamp', timezone.now())
                        )
                        processed_data['gps'] += 1
                    except Animal.DoesNotExist:
                        continue
            
            # Procesar datos de salud en lote
            if 'health_data' in serializer.validated_data:
                for health_item in serializer.validated_data['health_data']:
                    try:
                        animal = Animal.objects.get(ear_tag=health_item['animal_ear_tag'])
                        HealthSensorData.objects.create(
                            device=device,
                            animal=animal,
                            heart_rate=health_item.get('heart_rate'),
                            temperature=health_item.get('temperature'),
                            movement_activity=health_item.get('movement_activity'),
                            timestamp=health_item.get('timestamp', timezone.now())
                        )
                        processed_data['health'] += 1
                    except Animal.DoesNotExist:
                        continue
            
            device.last_reading = timezone.now()
            device.save()
            
            return Response({
                'status': 'success',
                'processed': processed_data,
                'device_id': device.device_id
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeviceRegistrationView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = DeviceRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            
            # Verificar si el dispositivo ya existe
            if IoTDevice.objects.filter(device_id=data['device_id']).exists():
                return Response({
                    'error': 'Ya existe un dispositivo con este ID'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Crear dispositivo
            device_data = {
                'device_id': data['device_id'],
                'device_type': data['device_type'],
                'name': data['name'],
                'description': data.get('description', ''),
                'firmware_version': data.get('firmware_version', '1.0.0'),
                'mac_address': data.get('mac_address', ''),
                'owner': request.user
            }
            
            # Asociar animal si se proporciona
            if data.get('animal_ear_tag'):
                try:
                    animal = Animal.objects.get(ear_tag=data['animal_ear_tag'], owner=request.user)
                    device_data['animal'] = animal
                except Animal.DoesNotExist:
                    return Response({
                        'error': f'Animal con ear_tag {data["animal_ear_tag"]} no encontrado'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            device = IoTDevice.objects.create(**device_data)
            
            # Crear configuración por defecto
            DeviceConfiguration.objects.create(device=device)
            
            return Response({
                'success': True,
                'device_id': device.device_id,
                'message': 'Dispositivo registrado correctamente'
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class IoTStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = None  # Esta vista no usa serializer
    
    def get(self, request):
        stats = {
            'total_devices': IoTDevice.objects.filter(owner=request.user).count(),
            'active_devices': IoTDevice.objects.filter(owner=request.user, status='ACTIVE').count(),
            'total_gps_data': GPSData.objects.filter(animal__owner=request.user).count(),
            'total_health_data': HealthSensorData.objects.filter(animal__owner=request.user).count(),
            'health_alerts': HealthSensorData.objects.filter(animal__owner=request.user, health_alert=True).count(),
            'devices_by_type': dict(IoTDevice.objects.filter(owner=request.user)
                                  .values_list('device_type')
                                  .annotate(count=Count('id'))),
            'recent_events': DeviceEvent.objects.filter(device__owner=request.user)
                              .order_by('-timestamp')[:5].count()
        }
        
        return Response(stats)