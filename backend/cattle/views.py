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
        
        if not self.request.user.is_superuser:
            queryset = queryset.filter(owner=self.request.user)
        
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
        if 'owner' not in serializer.validated_data:
            serializer.save(owner=self.request.user)
        else:
            serializer.save()
    
    @action(detail=True, methods=['post'])
    def mint_nft(self, request, pk=None):
        try:
            animal = self.get_object()
            
            if animal.token_id:
                return Response({
                    'success': False,
                    'error': f'El animal {animal.ear_tag} ya tiene un NFT (Token ID: {animal.token_id})'
                }, status=status.HTTP_400_BAD_REQUEST)
            
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
            
            from blockchain.services import BlockchainService
            service = BlockchainService()
            result = service.mint_and_associate_animal(
                animal=animal,
                owner_wallet=owner_wallet,
                operational_ipfs=operational_ipfs
            )
            
            if result['success']:
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
        try:
            animal = self.get_object()
            
            if not animal.token_id:
                return Response({
                    'success': False,
                    'error': f'El animal {animal.ear_tag} no tiene NFT asociado'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            from blockchain.services import BlockchainService
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
            }, status=status.HTTP_500_INternalServerError)
    
    @action(detail=True, methods=['get'])
    def nft_info(self, request, pk=None):
        try:
            animal = self.get_object()
            
            if not animal.token_id:
                return Response({
                    'success': False,
                    'error': f'El animal {animal.ear_tag} no tiene NFT asociado'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            from blockchain.services import BlockchainService
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
        
        if not self.request.user.is_superuser:
            queryset = queryset.filter(
                Q(animal__owner=self.request.user) | 
                Q(veterinarian=self.request.user)
            )
        
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
        
        if not self.request.user.is_superuser:
            queryset = queryset.filter(created_by=self.request.user)
        
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
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_animals(self, request, pk=None):
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cattle_stats(request):
    user = request.user
    if user.is_superuser:
        animals = Animal.objects.all()
        batches = Batch.objects.all()
    else:
        animals = Animal.objects.filter(owner=user)
        batches = Batch.objects.filter(created_by=user)
    
    from collections import defaultdict
    stats = {
        'total_animals': animals.count(),
        'minted_animals': animals.filter(token_id__isnull=False).count(),
        'total_batches': batches.count(),
        'animals_by_health_status': defaultdict(int),
        'batches_by_status': defaultdict(int)
    }
    
    for status_val, count in animals.values_list('health_status').annotate(count=Count('id')):
        stats['animals_by_health_status'][status_val] = count
    
    for status_val, count in batches.values_list('status').annotate(count=Count('id')):
        stats['batches_by_status'][status_val] = count
    
    return Response(stats)