from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from .models import SmartContract, NetworkState
from .serializers import SmartContractSerializer
from .services import BlockchainService
import logging

logger = logging.getLogger(__name__)

class SmartContractAdminView(viewsets.ModelViewSet):
    queryset = SmartContract.objects.all()
    serializer_class = SmartContractSerializer
    permission_classes = [IsAdminUser]
    
    @action(detail=True, methods=['post'])
    def upgrade(self, request, pk=None):
        contract = self.get_object()
        new_address = request.data.get('new_address')
        new_abi = request.data.get('new_abi')
        
        if not new_address:
            return Response({'error': 'Nueva dirección requerida'}, status=400)
        
        try:
            blockchain_service = BlockchainService()
            result = blockchain_service.upgrade_contract(
                contract.address, new_address, new_abi
            )
            
            if result['success']:
                contract.address = new_address
                if new_abi:
                    contract.abi = new_abi
                contract.save()
                
                return Response({
                    'success': True,
                    'message': 'Contrato actualizado',
                    'new_address': new_address
                })
            else:
                return Response({
                    'error': result.get('error', 'Error desconocido')
                }, status=400)
                
        except Exception as e:
            return Response({'error': str(e)}, status=400)

class EventSubscriptionView(APIView):
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        event_name = request.data.get('event_name')
        contract_address = request.data.get('contract_address')
        from_block = request.data.get('from_block')
        
        if not event_name or not contract_address:
            return Response({
                'error': 'event_name y contract_address requeridos'
            }, status=400)
        
        try:
            blockchain_service = BlockchainService()
            result = blockchain_service.subscribe_to_event(
                event_name, contract_address, from_block
            )
            
            return Response(result)
            
        except Exception as e:
            return Response({'error': str(e)}, status=400)

class GasOptimizationView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        blockchain_service = BlockchainService()
        
        try:
            current_gas = blockchain_service.w3.eth.gas_price
            suggested_gas = int(current_gas * 0.9)  # 10% menos
            
            gas_stats = {
                'current_gas_price': current_gas,
                'current_gas_gwei': blockchain_service.w3.from_wei(current_gas, 'gwei'),
                'suggested_gas_price': suggested_gas,
                'suggested_gas_gwei': blockchain_service.w3.from_wei(suggested_gas, 'gwei'),
                'estimated_savings': current_gas - suggested_gas,
                'estimated_savings_gwei': blockchain_service.w3.from_wei(current_gas - suggested_gas, 'gwei')
            }
            
            return Response(gas_stats)
            
        except Exception as e:
            return Response({'error': str(e)}, status=400)

class CrossChainView(APIView):
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        # Placeholder para integración cross-chain
        # Esto requeriría bridges como Polygon Bridge, etc.
        
        return Response({
            'message': 'Funcionalidad cross-chain en desarrollo',
            'supported_chains': ['Polygon', 'Ethereum', 'Binance Smart Chain']
        })
