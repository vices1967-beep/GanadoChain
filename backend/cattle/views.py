from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Animal, Batch
from .serializers import AnimalSerializer, BatchSerializer
from blockchain.services import BlockchainService

User = get_user_model()

class AnimalListCreateView(generics.ListCreateAPIView):
    queryset = Animal.objects.all()
    serializer_class = AnimalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Asegurar que el owner sea el usuario autenticado si no se especifica
        if 'owner' not in serializer.validated_data:
            serializer.save(owner=self.request.user)
        else:
            serializer.save()

class AnimalDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Animal.objects.all()
    serializer_class = AnimalSerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mint_animal_nft(request, pk):
    """
    Endpoint para mintear NFT de un animal
    """
    try:
        animal = get_object_or_404(Animal, pk=pk)
        
        # Validar que el animal no tenga ya un NFT
        if animal.token_id:
            return Response({
                'success': False,
                'error': f'El animal {animal.ear_tag} ya tiene un NFT (Token ID: {animal.token_id})'
            }, status=400)
        
        # Validar que tenga IPFS hash
        if not animal.ipfs_hash:
            return Response({
                'success': False,
                'error': f'El animal {animal.ear_tag} no tiene IPFS hash configurado'
            }, status=400)
        
        # Obtener wallet del request o usar la del usuario
        owner_wallet = request.data.get('owner_wallet')
        if not owner_wallet:
            # Usar wallet del usuario si no se especifica
            if not request.user.wallet_address:
                return Response({
                    'success': False,
                    'error': 'No se especificó owner_wallet y el usuario no tiene wallet address configurada'
                }, status=400)
            owner_wallet = request.user.wallet_address
        
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
            }, status=400)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Error minting NFT: {str(e)}'
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_animal_nft(request, pk):
    """
    Endpoint para verificar el NFT de un animal
    """
    try:
        animal = get_object_or_404(Animal, pk=pk)
        
        if not animal.token_id:
            return Response({
                'success': False,
                'error': f'El animal {animal.ear_tag} no tiene NFT asociado'
            }, status=400)
        
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
        return Response({
            'success': False,
            'error': f'Error verifying NFT: {str(e)}'
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_animal_nft_info(request, pk):
    """
    Endpoint para obtener información del NFT de un animal
    """
    try:
        animal = get_object_or_404(Animal, pk=pk)
        
        if not animal.token_id:
            return Response({
                'success': False,
                'error': f'El animal {animal.ear_tag} no tiene NFT asociado'
            }, status=400)
        
        service = BlockchainService()
        nft_info = service.get_animal_nft_info(animal)
        
        return Response({
            'success': True,
            'animal_id': animal.id,
            'ear_tag': animal.ear_tag,
            'nft_info': nft_info
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Error getting NFT info: {str(e)}'
        }, status=500)

class BatchListCreateView(generics.ListCreateAPIView):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Asignar el usuario autenticado como creador
        serializer.save(created_by=self.request.user)

class BatchDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer
    permission_classes = [permissions.IsAuthenticated]