from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from .models import Animal, AnimalHealthRecord, Batch
from .serializers import (
    AnimalSerializer, 
    AnimalHealthRecordSerializer, 
    BatchSerializer, 
    BatchCreateSerializer,
    AnimalMintSerializer,
    HealthDataSerializer
)
from iot.models import IoTDevice  # Importar desde la app iot
from iot.serializers import IoTDeviceSerializer  # Importar serializer desde iot si es necesario
from blockchain.services import BlockchainService
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class AnimalViewSet(viewsets.ModelViewSet):
    queryset = Animal.objects.all()
    serializer_class = AnimalSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, JSONParser]
    
    def get_queryset(self):
        queryset = Animal.objects.all()
        
        # Filtrar por owner si no es superuser
        if not self.request.user.is_superuser:
            queryset = queryset.filter(owner=self.request.user)
        
        # Filtros adicionales
        ear_tag = self.request.query_params.get('ear_tag', None)
        breed = self.request.query_params.get('breed', None)
        health_status = self.request.query_params.get('health_status', None)
        minted = self.request.query_params.get('minted', None)
        
        if ear_tag:
            queryset = queryset.filter(ear_tag__icontains=ear_tag)
        if breed:
            queryset = queryset.filter(breed__icontains=breed)
        if health_status:
            queryset = queryset.filter(health_status=health_status)
        if minted == 'true':
            queryset = queryset.filter(token_id__isnull=False)
        elif minted == 'false':
            queryset = queryset.filter(token_id__isnull=True)
            
        return queryset
    
    def perform_create(self, serializer):
        # Asegurar que el owner sea el usuario autenticado si no se especifica
        if 'owner' not in serializer.validated_data:
            serializer.save(owner=self.request.user)
        else:
            serializer.save()
    
    @action(detail=True, methods=['post'])
    def mint_nft(self, request, pk=None):
        """
        Endpoint para mintear NFT de un animal
        """
        try:
            animal = self.get_object()
            
            # Validar que el animal no tenga ya un NFT
            if animal.token_id:
                return Response({
                    'success': False,
                    'error': f'El animal {animal.ear_tag} ya tiene un NFT (Token ID: {animal.token_id})'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validar que tenga IPFS hash
            if not animal.ipfs_hash:
                return Response({
                    'success': False,
                    'error': f'El animal {animal.ear_tag} no tiene IPFS hash configurado'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = AnimalMintSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'error': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            owner_wallet = serializer.validated_data['wallet_address']
            operational_ipfs = request.data.get('operational_ipfs', '')
            
            # Llamar al servicio de blockchain
            service = BlockchainService()
            result = service.mint_and_associate_animal(
                animal=animal,
                owner_wallet=owner_wallet,
                operational_ipfs=operational_ipfs
            )
            
            if result['success']:
                # Recargar el animal para obtener los datos actualizados
                animal.refresh_from_db()
                return Response({
                    'success': True,
                    'message': f'NFT minted successfully for {animal.ear_tag}',
                    'animal_id': animal.id,
                    'ear_tag': animal.ear_tag,
                    'token_id': result['token_id'],
                    'transaction_hash': result['tx_hash'],
                    'owner_wallet': result['owner_wallet'],
                    'nft_owner_wallet': animal.nft_owner_wallet,
                    'mint_transaction_hash': animal.mint_transaction_hash
                })
            else:
                return Response({
                    'success': False,
                    'error': result['error'],
                    'animal_id': animal.id,
                    'ear_tag': animal.ear_tag
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error minting NFT for animal {pk}: {str(e)}")
            return Response({
                'success': False,
                'error': f'Error minting NFT: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def verify_nft(self, request, pk=None):
        """
        Endpoint para verificar el NFT de un animal
        """
        try:
            animal = self.get_object()
            
            if not animal.token_id:
                return Response({
                    'success': False,
                    'error': f'El animal {animal.ear_tag} no tiene NFT asociado'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            service = BlockchainService()
            verification = service.verify_animal_nft(animal)
            
            return Response({
                'success': True,
                'animal_id': animal.id,
                'ear_tag': animal.ear_tag,
                'token_id': animal.token_id,
                'verification': verification
            })
            
        except Exception as e:
            logger.error(f"Error verifying NFT for animal {pk}: {str(e)}")
            return Response({
                'success': False,
                'error': f'Error verifying NFT: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def nft_info(self, request, pk=None):
        """
        Endpoint para obtener información del NFT de un animal
        """
        try:
            animal = self.get_object()
            
            if not animal.token_id:
                return Response({
                    'success': False,
                    'error': f'El animal {animal.ear_tag} no tiene NFT asociado'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            service = BlockchainService()
            nft_info = service.get_animal_nft_info(animal)
            
            return Response({
                'success': True,
                'animal_id': animal.id,
                'ear_tag': animal.ear_tag,
                'nft_info': nft_info
            })
            
        except Exception as e:
            logger.error(f"Error getting NFT info for animal {pk}: {str(e)}")
            return Response({
                'success': False,
                'error': f'Error getting NFT info: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def health_records(self, request, pk=None):
        """
        Obtener todos los registros de salud de un animal
        """
        animal = self.get_object()
        records = animal.health_records.all().order_by('-created_at')
        serializer = AnimalHealthRecordSerializer(records, many=True)
        return Response(serializer.data)

class AnimalHealthRecordViewSet(viewsets.ModelViewSet):
    queryset = AnimalHealthRecord.objects.all()
    serializer_class = AnimalHealthRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = AnimalHealthRecord.objects.all()
        
        # Filtrar por permisos de usuario
        if not self.request.user.is_superuser:
            queryset = queryset.filter(
                Q(animal__owner=self.request.user) | 
                Q(veterinarian=self.request.user)
            )
        
        # Filtros adicionales
        animal_id = self.request.query_params.get('animal_id', None)
        health_status = self.request.query_params.get('health_status', None)
        source = self.request.query_params.get('source', None)
        iot_device = self.request.query_params.get('iot_device', None)
        
        if animal_id:
            queryset = queryset.filter(animal_id=animal_id)
        if health_status:
            queryset = queryset.filter(health_status=health_status)
        if source:
            queryset = queryset.filter(source=source)
        if iot_device:
            queryset = queryset.filter(iot_device_id=iot_device)
            
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        # Asignar veterinario si no se especifica y el usuario es veterinario
        if 'veterinarian' not in serializer.validated_data and hasattr(self.request.user, 'is_veterinarian'):
            serializer.save(veterinarian=self.request.user)
        else:
            serializer.save()

class BatchViewSet(viewsets.ModelViewSet):
    queryset = Batch.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return BatchCreateSerializer
        return BatchSerializer
    
    def get_queryset(self):
        queryset = Batch.objects.all()
        
        # Filtrar por creador si no es superuser
        if not self.request.user.is_superuser:
            queryset = queryset.filter(created_by=self.request.user)
        
        # Filtros adicionales
        status_filter = self.request.query_params.get('status', None)
        name = self.request.query_params.get('name', None)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if name:
            queryset = queryset.filter(name__icontains=name)
            
        return queryset.annotate(
            animals_count=Count('animals'),
            minted_animals_count=Count('animals', filter=Q(animals__token_id__isnull=False))
        )
    
    def perform_create(self, serializer):
        # Asignar el usuario autenticado como creador
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_animals(self, request, pk=None):
        """
        Añadir animales a un lote existente
        """
        batch = self.get_object()
        animal_ids = request.data.get('animal_ids', [])
        
        if not animal_ids:
            return Response({
                'error': 'Se requiere una lista de animal_ids'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            animals = Animal.objects.filter(id__in=animal_ids, owner=request.user)
            batch.animals.add(*animals)
            batch.save()
            
            return Response({
                'success': True,
                'message': f'{animals.count()} animales añadidos al lote',
                'batch_id': batch.id,
                'batch_name': batch.name
            })
            
        except Exception as e:
            return Response({
                'error': f'Error añadiendo animales: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def remove_animals(self, request, pk=None):
        """
        Remover animales de un lote existente
        """
        batch = self.get_object()
        animal_ids = request.data.get('animal_ids', [])
        
        if not animal_ids:
            return Response({
                'error': 'Se requiere una lista de animal_ids'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            animals = Animal.objects.filter(id__in=animal_ids)
            batch.animals.remove(*animals)
            batch.save()
            
            return Response({
                'success': True,
                'message': f'{len(animal_ids)} animales removidos del lote',
                'batch_id': batch.id,
                'batch_name': batch.name
            })
            
        except Exception as e:
            return Response({
                'error': f'Error removiendo animales: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

class IoTDeviceViewSet(viewsets.ModelViewSet):
    queryset = IoTDevice.objects.all()
    serializer_class = IoTDeviceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = IoTDevice.objects.all()
        
        # Filtrar por permisos de usuario
        if not self.request.user.is_superuser:
            queryset = queryset.filter(
                Q(animal__owner=self.request.user) | 
                Q(animal__isnull=True)
            )
        
        # Filtros adicionales
        device_type = self.request.query_params.get('device_type', None)
        status = self.request.query_params.get('status', None)
        animal_id = self.request.query_params.get('animal_id', None)
        
        if device_type:
            queryset = queryset.filter(device_type=device_type)
        if status:
            queryset = queryset.filter(status=status)
        if animal_id:
            queryset = queryset.filter(animal_id=animal_id)
            
        return queryset
    
    @action(detail=False, methods=['post'])
    def health_data(self, request):
        """
        Endpoint para recepción de datos de salud desde dispositivos IoT
        """
        serializer = HealthDataSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            # Buscar el animal por ear_tag
            animal = Animal.objects.get(ear_tag=data['animal_ear_tag'])
            
            # Crear registro de salud
            health_record = AnimalHealthRecord.objects.create(
                animal=animal,
                health_status=Animal.HealthStatus.HEALTHY,  # Se puede ajustar basado en valores
                source='IOT_SENSOR',
                iot_device_id=data['device_id'],
                temperature=data.get('temperature'),
                heart_rate=data.get('heart_rate'),
                movement_activity=data.get('movement_activity')
            )
            
            # Actualizar dispositivo IoT si existe
            device, created = IoTDevice.objects.get_or_create(
                device_id=data['device_id'],
                defaults={
                    'device_type': 'MULTI',
                    'status': 'ACTIVE',
                    'animal': animal,
                    'battery_level': data.get('battery_level'),
                    'last_reading': data.get('timestamp')
                }
            )
            
            if not created:
                device.battery_level = data.get('battery_level')
                device.last_reading = data.get('timestamp')
                device.save()
            
            return Response({
                'success': True,
                'health_record_id': health_record.id,
                'animal_id': animal.id,
                'device_id': data['device_id']
            })
            
        except Animal.DoesNotExist:
            return Response({
                'error': f'Animal con ear_tag {data["animal_ear_tag"]} no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error procesando datos IoT: {str(e)}")
            return Response({
                'error': f'Error procesando datos: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cattle_stats(request):
    """
    Endpoint para obtener estadísticas del ganado
    """
    user = request.user
    if user.is_superuser:
        animals = Animal.objects.all()
        batches = Batch.objects.all()
    else:
        animals = Animal.objects.filter(owner=user)
        batches = Batch.objects.filter(created_by=user)
    
    stats = {
        'total_animals': animals.count(),
        'minted_animals': animals.filter(token_id__isnull=False).count(),
        'total_batches': batches.count(),
        'animals_by_health_status': dict(animals.values_list('health_status').annotate(count=Count('id'))),
        'batches_by_status': dict(batches.values_list('status').annotate(count=Count('id')))
    }
    
    return Response(stats)