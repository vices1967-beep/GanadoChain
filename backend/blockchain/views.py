from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from .services import BlockchainService
from .models import BlockchainEvent, ContractInteraction, NetworkState, SmartContract, GasPriceHistory, TransactionPool
from .serializers import (
    AssignRoleSerializer, MintNFTSerializer,
    RegisterAnimalSerializer, CheckRoleSerializer,
    MintTokensSerializer, UpdateHealthSerializer,
    IoTHealthDataSerializer, AnimalHistorySerializer,
    BatchCreateSerializer, ContractCallSerializer,
    NetworkStatusSerializer, TransactionStatusSerializer,
    GasPriceSerializer, EventSubscriptionSerializer,
    WebhookSerializer, BlockchainEventSerializer,
    ContractInteractionSerializer, NetworkStateSerializer,
    SmartContractSerializer, GasPriceHistorySerializer,
    TransactionPoolSerializer, BlockchainStatsSerializer
)
from cattle.models import Animal, HealthStatus
import logging

logger = logging.getLogger(__name__)

class BlockchainEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BlockchainEvent.objects.all()
    serializer_class = BlockchainEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = BlockchainEvent.objects.all()
        
        # Filtros
        event_type = self.request.query_params.get('event_type', None)
        animal_id = self.request.query_params.get('animal_id', None)
        batch_id = self.request.query_params.get('batch_id', None)
        from_address = self.request.query_params.get('from_address', None)
        block_number = self.request.query_params.get('block_number', None)
        
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        if animal_id:
            queryset = queryset.filter(animal_id=animal_id)
        if batch_id:
            queryset = queryset.filter(batch_id=batch_id)
        if from_address:
            queryset = queryset.filter(from_address__iexact=from_address)
        if block_number:
            queryset = queryset.filter(block_number=block_number)
            
        return queryset.order_by('-block_number', '-created_at')
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Obtener los eventos más recientes"""
        limit = int(request.query_params.get('limit', 10))
        events = self.get_queryset()[:limit]
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)

class ContractInteractionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ContractInteraction.objects.all()
    serializer_class = ContractInteractionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = ContractInteraction.objects.all()
        
        # Filtros
        contract_type = self.request.query_params.get('contract_type', None)
        action_type = self.request.query_params.get('action_type', None)
        status = self.request.query_params.get('status', None)
        caller_address = self.request.query_params.get('caller_address', None)
        
        if contract_type:
            queryset = queryset.filter(contract_type=contract_type)
        if action_type:
            queryset = queryset.filter(action_type=action_type)
        if status:
            queryset = queryset.filter(status=status)
        if caller_address:
            queryset = queryset.filter(caller_address__iexact=caller_address)
            
        return queryset.order_by('-block_number', '-created_at')
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estadísticas de interacciones con contratos"""
        stats = {
            'total_interactions': ContractInteraction.objects.count(),
            'successful_interactions': ContractInteraction.objects.filter(status='SUCCESS').count(),
            'failed_interactions': ContractInteraction.objects.filter(status='FAILED').count(),
            'pending_interactions': ContractInteraction.objects.filter(status='PENDING').count(),
            'by_contract_type': dict(ContractInteraction.objects.values_list('contract_type').annotate(count=Count('id'))),
            'by_action_type': dict(ContractInteraction.objects.values_list('action_type').annotate(count=Count('id')))
        }
        return Response(stats)

class SmartContractViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SmartContract.objects.filter(is_active=True)
    serializer_class = SmartContractSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = SmartContract.objects.filter(is_active=True)
        
        contract_type = self.request.query_params.get('contract_type', None)
        if contract_type:
            queryset = queryset.filter(contract_type=contract_type)
            
        return queryset

class AssignRoleView(generics.CreateAPIView):
    serializer_class = AssignRoleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        blockchain_service = BlockchainService()
        try:
            result = blockchain_service.assign_role(
                serializer.validated_data['target_wallet'],
                serializer.validated_data['role']
            )
            
            if result['success']:
                return Response({
                    'success': True,
                    'tx_hash': result['tx_hash'],
                    'message': 'Rol asignado correctamente',
                    'role': serializer.validated_data['role'],
                    'target_wallet': serializer.validated_data['target_wallet']
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'error': result.get('error', 'Error desconocido')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error assigning role: {str(e)}")
            return Response({
                'success': False,
                'error': f'Error asignando rol: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

class MintNFTView(generics.CreateAPIView):
    serializer_class = MintNFTSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        blockchain_service = BlockchainService()
        try:
            # Verificar que el animal existe
            animal = get_object_or_404(Animal, id=serializer.validated_data['animal_id'])
            
            result = blockchain_service.mint_animal_nft(
                animal=animal,
                owner_wallet=serializer.validated_data['owner_wallet'],
                metadata_uri=serializer.validated_data['metadata_uri'],
                operational_ipfs=serializer.validated_data.get('operational_ipfs', '')
            )
            
            if result['success']:
                return Response({
                    'success': True,
                    'tx_hash': result['tx_hash'],
                    'token_id': result['token_id'],
                    'message': 'NFT minted correctamente',
                    'animal_id': animal.id,
                    'ear_tag': animal.ear_tag
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'error': result.get('error', 'Error desconocido'),
                    'animal_id': animal.id
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Animal.DoesNotExist:
            return Response({
                'success': False,
                'error': f'Animal con ID {serializer.validated_data["animal_id"]} no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error minting NFT: {str(e)}")
            return Response({
                'success': False,
                'error': f'Error minting NFT: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

class CheckRoleView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CheckRoleSerializer

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
            logger.error(f"Error checking role: {str(e)}")
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
            result = blockchain_service.mint_tokens(
                serializer.validated_data['to_wallet'],
                serializer.validated_data['amount'],
                serializer.validated_data.get('batch_id', '')
            )
            
            if result['success']:
                return Response({
                    'success': True,
                    'tx_hash': result['tx_hash'],
                    'message': 'Tokens minted correctamente',
                    'amount': serializer.validated_data['amount'],
                    'to_wallet': serializer.validated_data['to_wallet']
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'error': result.get('error', 'Error desconocido')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error minting tokens: {str(e)}")
            return Response({
                'success': False,
                'error': f'Error minting tokens: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

class AnimalHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AnimalHistorySerializer
    
    def get(self, request, animal_id):
        blockchain_service = BlockchainService()
        try:
            # Verificar que el animal existe
            animal = get_object_or_404(Animal, id=animal_id)
            
            # Obtener historial de blockchain
            blockchain_history = blockchain_service.get_animal_history(animal_id)
            
            # Obtener eventos relacionados de la base de datos
            events = BlockchainEvent.objects.filter(animal=animal).order_by('-block_number')
            event_serializer = BlockchainEventSerializer(events, many=True)
            
            return Response({
                'success': True,
                'animal_id': animal_id,
                'ear_tag': animal.ear_tag,
                'blockchain_history': blockchain_history,
                'events': event_serializer.data,
                'total_events': events.count()
            })
        except Animal.DoesNotExist:
            return Response({
                'success': False,
                'error': f'Animal con ID {animal_id} no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error getting animal history: {str(e)}")
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
            # Verificar que el animal existe
            animal = get_object_or_404(Animal, id=data['animal_id'])
            
            result = blockchain_service.update_animal_health(
                animal_id=data['animal_id'],
                health_status=data['health_status'],
                veterinarian_wallet=data.get('veterinarian_wallet', ''),
                notes=data.get('notes', ''),
                source=data['source'],
                temperature=data.get('temperature'),
                heart_rate=data.get('heart_rate'),
                movement_activity=data.get('movement_activity')
            )
            
            if result['success']:
                return Response({
                    'success': True,
                    'tx_hash': result['tx_hash'],
                    'message': 'Estado de salud actualizado correctamente',
                    'animal_id': animal.id,
                    'ear_tag': animal.ear_tag,
                    'health_status': data['health_status']
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'error': result.get('error', 'Error desconocido'),
                    'animal_id': animal.id
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Animal.DoesNotExist:
            return Response({
                'success': False,
                'error': f'Animal con ID {data["animal_id"]} no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error updating health: {str(e)}")
            return Response({
                'success': False,
                'error': f'Error actualizando salud: {str(e)}'
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
            try:
                animal = Animal.objects.get(ear_tag=data['animal_ear_tag'])
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
            
            if data.get('heart_rate') and (data['heart_rate'] < 50 or data['heart_rate'] > 100):
                health_status = HealthStatus.UNDER_OBSERVATION
                notes += " - Ritmo cardíaco anormal"
            
            result = blockchain_service.update_health_from_iot(
                animal.id,
                health_status,
                data['device_id'],
                data.get('temperature'),
                data.get('heart_rate'),
                data.get('movement_activity'),
                notes
            )
            
            if result['success']:
                return Response({
                    'success': True,
                    'tx_hash': result['tx_hash'],
                    'health_status': health_status,
                    'message': 'Datos de salud procesados correctamente',
                    'animal_id': animal.id,
                    'ear_tag': animal.ear_tag,
                    'device_id': data['device_id']
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'error': result.get('error', 'Error desconocido'),
                    'animal_id': animal.id
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error processing IoT data: {str(e)}")
            return Response({
                'success': False,
                'error': f'Error procesando datos IoT: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

class NetworkStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NetworkStatusSerializer
    
    def get(self, request, *args, **kwargs):
        blockchain_service = BlockchainService()
        try:
            balance = blockchain_service.get_balance()
            last_block = blockchain_service.w3.eth.block_number
            gas_price = blockchain_service.w3.eth.gas_price
            
            # Obtener estado de la red desde la base de datos
            network_state = NetworkState.objects.first()
            network_serializer = NetworkStateSerializer(network_state)
            
            return Response({
                'success': True,
                'network_status': {
                    'chain_id': blockchain_service.w3.eth.chain_id,
                    'block_number': last_block,
                    'gas_price': gas_price,
                    'gas_price_gwei': blockchain_service.w3.from_wei(gas_price, 'gwei'),
                    'account_balance': balance,
                    'account_balance_eth': blockchain_service.w3.from_wei(balance, 'ether'),
                    'account_address': blockchain_service.wallet_address
                },
                'network_state': network_serializer.data
            })
        except Exception as e:
            logger.error(f"Error getting network status: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class TransactionStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TransactionStatusSerializer
    
    def get(self, request, tx_hash):
        blockchain_service = BlockchainService()
        try:
            # Normalizar hash de transacción
            if not tx_hash.startswith('0x'):
                tx_hash = '0x' + tx_hash
            
            # Buscar en la base de datos primero
            try:
                interaction = ContractInteraction.objects.get(transaction_hash=tx_hash)
                serializer = ContractInteractionSerializer(interaction)
                return Response({
                    'success': True,
                    'from_db': True,
                    'transaction': serializer.data
                })
            except ContractInteraction.DoesNotExist:
                pass
            
            # Si no está en la base de datos, consultar la blockchain
            try:
                receipt = blockchain_service.w3.eth.get_transaction_receipt(tx_hash)
                if receipt:
                    status = 'CONFIRMED' if receipt['status'] == 1 else 'FAILED'
                    return Response({
                        'success': True,
                        'from_db': False,
                        'transaction_hash': tx_hash,
                        'status': status,
                        'block_number': receipt['blockNumber'],
                        'gas_used': receipt['gasUsed'],
                        'gas_price': receipt.get('effectiveGasPrice', 0),
                        'confirmations': blockchain_service.w3.eth.block_number - receipt['blockNumber']
                    })
                else:
                    # Buscar en la pool de transacciones pendientes
                    try:
                        pending_tx = TransactionPool.objects.get(transaction_hash=tx_hash)
                        pool_serializer = TransactionPoolSerializer(pending_tx)
                        return Response({
                            'success': True,
                            'from_db': True,
                            'status': 'PENDING',
                            'transaction': pool_serializer.data
                        })
                    except TransactionPool.DoesNotExist:
                        return Response({
                            'success': True,
                            'from_db': False,
                            'transaction_hash': tx_hash,
                            'status': 'PENDING',
                            'message': 'Transacción pendiente de confirmación'
                        })
            except Exception as e:
                return Response({
                    'success': False,
                    'error': f'Error consultando transacción: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error getting transaction status: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class GasPriceView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GasPriceSerializer
    
    def get(self, request, *args, **kwargs):
        blockchain_service = BlockchainService()
        try:
            gas_price = blockchain_service.w3.eth.gas_price
            
            # Obtener historial de precios de gas
            gas_history = GasPriceHistory.objects.order_by('-timestamp')[:10]
            history_serializer = GasPriceHistorySerializer(gas_history, many=True)
            
            return Response({
                'success': True,
                'current_gas_price': {
                    'wei': gas_price,
                    'gwei': blockchain_service.w3.from_wei(gas_price, 'gwei'),
                    'eth': blockchain_service.w3.from_wei(gas_price, 'ether')
                },
                'gas_price_history': history_serializer.data
            })
        except Exception as e:
            logger.error(f"Error getting gas price: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class BlockchainStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BlockchainStatsSerializer
    
    def get(self, request, *args, **kwargs):
        try:
            from django.db import models
            
            stats = {
                'total_events': BlockchainEvent.objects.count(),
                'total_transactions': ContractInteraction.objects.count(),
                'successful_transactions': ContractInteraction.objects.filter(status='SUCCESS').count(),
                'failed_transactions': ContractInteraction.objects.filter(status='FAILED').count(),
                'average_gas_price': GasPriceHistory.objects.aggregate(avg_gas=models.Avg('gas_price'))['avg_gas'] or 0,
                'total_gas_used': ContractInteraction.objects.aggregate(total_gas=models.Sum('gas_used'))['total_gas'] or 0,
                'last_block_number': NetworkState.objects.first().last_block_number if NetworkState.objects.exists() else 0,
                'active_contracts': SmartContract.objects.filter(is_active=True).count(),
                'pending_transactions': TransactionPool.objects.filter(status='PENDING').count(),
                'events_by_type': dict(BlockchainEvent.objects.values_list('event_type').annotate(count=Count('id'))),
                'interactions_by_type': dict(ContractInteraction.objects.values_list('contract_type').annotate(count=Count('id')))
            }
            
            serializer = BlockchainStatsSerializer(stats)
            return Response({
                'success': True,
                'stats': serializer.data
            })
            
        except Exception as e:
            logger.error(f"Error getting blockchain stats: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
class BatchCreateView(generics.CreateAPIView):
    """Vista para crear lotes en blockchain"""
    serializer_class = BatchCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        blockchain_service = BlockchainService()
        try:
            result = blockchain_service.create_batch(
                serializer.validated_data['name'],
                serializer.validated_data['description'],
                serializer.validated_data['animal_ids'],
                serializer.validated_data['creator_wallet']
            )
            
            if result['success']:
                return Response({
                    'success': True,
                    'tx_hash': result['tx_hash'],
                    'batch_id': result['batch_id'],
                    'message': 'Lote creado correctamente en blockchain',
                    'name': serializer.validated_data['name']
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'error': result.get('error', 'Error desconocido')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error creating batch: {str(e)}")
            return Response({
                'success': False,
                'error': f'Error creando lote: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)