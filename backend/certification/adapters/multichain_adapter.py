# backend/certification/adapters/multichain_adapter.py
from django.db import models
from core.multichain.manager import multichain_manager
from core.starknet.client import SyncStarknetClient
import json

class CertificationMultichainAdapter:
    """Adaptador para certificaciones multichain"""
    
    def __init__(self, certification):
        self.certification = certification
        
    def issue_on_blockchain(self, networks=None):
        """Emitir certificación en blockchain(s)"""
        if networks is None:
            networks = ['STARKNET_SEPOLIA', 'POLYGON_AMOY']
        
        results = {}
        for network_id in networks:
            network = multichain_manager.get_network(network_id)
            if network.is_starknet:
                results[network_id] = self._issue_on_starknet(network)
            else:
                results[network_id] = self._issue_on_evm(network)
        
        # Actualizar estado si al menos una fue exitosa
        if any(r['success'] for r in results.values()):
            self.certification.blockchain_certificate = True
            self.certification.save()
            
            # Crear registro multichain
            self._create_multichain_record(results)
        
        return results
    
    def _issue_on_starknet(self, network):
        """Emitir certificación en Starknet"""
        try:
            client = SyncStarknetClient(network)
            
            # Obtener contrato de certificaciones
            contract_address = self._get_certification_contract(network)
            
            # Preparar datos de la certificación
            cert_data = {
                'certificate_number': self.certification.certificate_number,
                'entity_address': self.certification.certified_entity.wallet_address,
                'standard_code': self.certification.standard.code,
                'grade': self.certification.grade,
                'issue_date': self.certification.issue_date.isoformat(),
                'expiry_date': self.certification.expiry_date.isoformat(),
            }
            
            # Llamar al contrato (implementación específica)
            # result = client.issue_certification(contract_address, cert_data)
            
            return {
                'success': True,
                'transaction_hash': '0x123...',  # Placeholder
                'network': network.name
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'network': network.name
            }
    
    def _issue_on_evm(self, network):
        """Emitir certificación en EVM (Polygon)"""
        # Implementación similar para EVM
        return {
            'success': True,
            'transaction_hash': '0x456...',  # Placeholder
            'network': network.name
        }
    
    def _get_certification_contract(self, network):
        """Obtener dirección del contrato de certificaciones"""
        # Lógica para obtener contrato según la red
        return "0xcontract_address"
    
    def _create_multichain_record(self, results):
        """Crear registro multichain para la certificación"""
        from core.multichain.models import ChainSpecificModel
        
        chain_data = {}
        for network_id, result in results.items():
            if result['success']:
                chain_data[network_id] = {
                    'transaction_hash': result['transaction_hash'],
                    'timestamp': result.get('timestamp')
                }
        
        multichain_record = ChainSpecificModel.objects.create(
            content_type='certification',
            object_id=str(self.certification.id),
            network=multichain_manager.get_primary_network(),
            chain_data=chain_data
        )
        
        self.certification.multichain_data = multichain_record
        self.certification.save()

class ConsumerAccessMultichainAdapter:
    """Adaptador para acceso multichain de consumidores"""
    
    def __init__(self, consumer_profile):
        self.consumer_profile = consumer_profile
    
    def process_payment(self, amount, cryptocurrency, network_id):
        """Procesar pago en la red especificada"""
        network = multichain_manager.get_network(network_id)
        
        if network.is_starknet:
            return self._process_starknet_payment(amount, cryptocurrency, network)
        else:
            return self._process_evm_payment(amount, cryptocurrency, network)
    
    def _process_starknet_payment(self, amount, cryptocurrency, network):
        """Procesar pago en Starknet"""
        # Implementación con starknet.py
        return {
            'success': True,
            'transaction_hash': '0x789...',
            'network': network.name
        }