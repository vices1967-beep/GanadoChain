# blockchain/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.conf import settings
from .services import BlockchainService
from .serializers import (
    AssignRoleSerializer, MintNFTSerializer,
    RegisterAnimalSerializer, CheckRoleSerializer,
    MintTokensSerializer, UpdateHealthSerializer,
    IoTHealthDataSerializer, AnimalHistorySerializer,
    BatchCreateSerializer, ContractInteractionSerializer,
    NetworkStatusSerializer, TransactionStatusSerializer,
    GasPriceSerializer, EventSubscriptionSerializer,
    WebhookSerializer
)

class AssignRoleView(generics.CreateAPIView):
    serializer_class = AssignRoleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        blockchain_service = BlockchainService()
        try:
            tx_hash = blockchain_service.assign_role(
                serializer.validated_data['target_wallet'],
                serializer.validated_data['role']
            )
            return Response({
                'success': True,
                'tx_hash': tx_hash,
                'message': 'Rol asignado correctamente'
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class MintNFTView(generics.CreateAPIView):
    serializer_class = MintNFTSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        blockchain_service = BlockchainService()
        try:
            tx_hash = blockchain_service.mint_animal_nft(
                serializer.validated_data['owner_wallet'],
                serializer.validated_data['metadata_uri'],
                serializer.validated_data.get('operational_ipfs', '')
            )
            return Response({
                'success': True,
                'tx_hash': tx_hash,
                'message': 'NFT minted correctamente'
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class RegisterAnimalView(generics.CreateAPIView):
    serializer_class = RegisterAnimalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        blockchain_service = BlockchainService()
        try:
            tx_hash = blockchain_service.register_animal_on_chain(
                serializer.validated_data['animal_id'],
                serializer.validated_data['metadata']
            )
            return Response({
                'success': True,
                'tx_hash': tx_hash,
                'message': 'Animal registrado en blockchain'
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class CheckRoleView(generics.RetrieveAPIView):
    serializer_class = CheckRoleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        wallet_address = request.query_params.get('wallet_address')
        role_name = request.query_params.get('role_name')
        
        if not wallet_address or not role_name:
            return Response({
                'success': False,
                'error': 'wallet_address and role_name parameters are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        blockchain_service = BlockchainService()
        try:
            has_role = blockchain_service.has_role(wallet_address, role_name)
            return Response({
                'success': True,
                'has_role': has_role,
                'wallet_address': wallet_address,
                'role_name': role_name
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class MintTokensView(generics.CreateAPIView):
    serializer_class = MintTokensSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        blockchain_service = BlockchainService()
        try:
            tx_hash = blockchain_service.mint_tokens(
                serializer.validated_data['to_wallet'],
                serializer.validated_data['amount']
            )
            return Response({
                'success': True,
                'tx_hash': tx_hash,
                'message': 'Tokens minted correctamente'
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class AnimalHistoryView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, animal_id):
        blockchain_service = BlockchainService()
        try:
            history = blockchain_service.get_transaction_history(animal_id)
            return Response({
                'success': True,
                'animal_id': animal_id,
                'history': history,
                'count': len(history)
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class UpdateHealthView(generics.CreateAPIView):
    serializer_class = UpdateHealthSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        blockchain_service = BlockchainService()
        data = serializer.validated_data
        
        try:
            source = data['source']
            
            if source == 'IOT_SENSOR':
                tx_hash = blockchain_service.update_health_from_iot(
                    data['animal_id'],
                    data['health_status'],
                    data['iot_device_id'],
                    data.get('temperature'),
                    data.get('heart_rate'),
                    data.get('notes', '')
                )
            else:
                tx_hash = blockchain_service.update_animal_health(
                    data['animal_id'],
                    data['health_status'],
                    data.get('veterinarian_wallet', ''),
                    data.get('notes', ''),
                    source,
                    data.get('temperature'),
                    data.get('heart_rate')
                )
            
            return Response({
                'success': True,
                'tx_hash': tx_hash,
                'message': 'Estado de salud actualizado correctamente'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class IoTHealthDataView(generics.CreateAPIView):
    serializer_class = IoTHealthDataSerializer
    permission_classes = [permissions.AllowAny]  # Para dispositivos IoT
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        blockchain_service = BlockchainService()
        data = serializer.validated_data
        
        try:
            # Convertir ear_tag a animal_id
            from cattle.models import Animal
            try:
                animal = Animal.objects.get(ear_tag=data['animal_ear_tag'])
                animal_id = animal.id
            except Animal.DoesNotExist:
                return Response({
                    'success': False,
                    'error': f'Animal con arete {data["animal_ear_tag"]} no encontrado'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Determinar estado de salud basado en datos IoT
            health_status = HealthStatus.HEALTHY
            notes = f"Datos IoT - Device: {data['device_id']}"
            
            if data.get('temperature') and data['temperature'] > 39.5:
                health_status = HealthStatus.SICK
                notes += " - Fiebre detectada"
            
            if data.get('heart_rate') and data['heart_rate'] < 50:
                health_status = HealthStatus.UNDER_OBSERVATION
                notes += " - Ritmo cardíaco bajo"
            
            tx_hash = blockchain_service.update_health_from_iot(
                animal_id,
                health_status,
                data['device_id'],
                data.get('temperature'),
                data.get('heart_rate'),
                notes
            )
            
            return Response({
                'success': True,
                'tx_hash': tx_hash,
                'health_status': health_status,
                'message': 'Datos de salud procesados correctamente'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class BatchCreateView(generics.CreateAPIView):
    serializer_class = BatchCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Esta funcionalidad sería implementada después
        return Response({
            'success': False,
            'error': 'Funcionalidad de batches no implementada aún'
        }, status=status.HTTP_501_NOT_IMPLEMENTED)

class NetworkStatusView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        blockchain_service = BlockchainService()
        try:
            balance = blockchain_service.get_balance()
            last_block = blockchain_service.w3.eth.block_number
            
            return Response({
                'success': True,
                'network_status': {
                    'chain_id': blockchain_service.w3.eth.chain_id,
                    'block_number': last_block,
                    'gas_price': blockchain_service.w3.eth.gas_price,
                    'account_balance': balance,
                    'account_address': blockchain_service.wallet_address
                }
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class TransactionStatusView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, tx_hash):
        blockchain_service = BlockchainService()
        try:
            receipt = blockchain_service.w3.eth.get_transaction_receipt(tx_hash)
            if receipt:
                status = 'CONFIRMED' if receipt['status'] == 1 else 'FAILED'
                return Response({
                    'success': True,
                    'transaction_hash': tx_hash,
                    'status': status,
                    'block_number': receipt['blockNumber'],
                    'gas_used': receipt['gasUsed'],
                    'confirmations': blockchain_service.w3.eth.block_number - receipt['blockNumber']
                })
            else:
                # Transacción pendiente
                return Response({
                    'success': True,
                    'transaction_hash': tx_hash,
                    'status': 'PENDING',
                    'message': 'Transacción pendiente de confirmación'
                })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class ContractInteractionView(generics.CreateAPIView):
    serializer_class = ContractInteractionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        return Response({
            'success': False,
            'error': 'Interacción directa con contratos no implementada'
        }, status=status.HTTP_501_NOT_IMPLEMENTED)

class GasPriceView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        blockchain_service = BlockchainService()
        try:
            gas_price = blockchain_service.w3.eth.gas_price
            return Response({
                'success': True,
                'gas_price': {
                    'standard': gas_price,
                    'gwei': blockchain_service.w3.from_wei(gas_price, 'gwei'),
                    'eth': blockchain_service.w3.from_wei(gas_price, 'ether')
                }
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)