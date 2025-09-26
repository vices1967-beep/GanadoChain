# backend/cattle/adapters/multichain_adapter.py
from django.db import models
from core.multichain.manager import multichain_manager
from core.starknet.client import SyncStarknetClient
import json

class AnimalMultichainAdapter:
    """Adaptador para integrar Animal existente con multichain"""
    
    def __init__(self, animal):
        self.animal = animal
        self.multichain_data, _ = animal.multichain_data.get_or_create(
            primary_network=multichain_manager.get_primary_network('STARKNET')
        )
    
    def mint_on_starknet(self, contract_address=None):
        """Mintear NFT del animal en Starknet"""
        starknet_network = multichain_manager.get_network('STARKNET_SEPOLIA')
        client = SyncStarknetClient(starknet_network)
        
        # Usar contrato por defecto si no se especifica
        if not contract_address:
            contract_address = self._get_default_contract_address()
        
        result = client.mint_animal_nft(self.animal, contract_address)
        
        if result['success']:
            # Actualizar datos multichain
            self.multichain_data.primary_token_id = result['token_id']
            self.multichain_data.save()
            
            # Crear registro de espejo
            from cattle.models import AnimalNFTMirror
            AnimalNFTMirror.objects.create(
                animal_multichain=self.multichain_data,
                network=starknet_network,
                token_id=result['token_id'],
                mirror_transaction_hash=result['transaction_hash']
            )
            
            # Actualizar animal original con hash de Starknet
            self.animal.starknet_transaction_hash = result['transaction_hash']
            self.animal.save()
        
        return result
    
    def mint_on_polygon(self):
        """Mintear NFT del animal en Polygon (compatibilidad hacia atrás)"""
        polygon_network = multichain_manager.get_network('POLYGON_AMOY')
        
        # Usar lógica existente de Polygon
        from blockchain.utils import mint_animal_nft
        result = mint_animal_nft(self.animal)
        
        if result['success']:
            # Crear registro de espejo
            from cattle.models import AnimalNFTMirror
            AnimalNFTMirror.objects.create(
                animal_multichain=self.multichain_data,
                network=polygon_network,
                token_id=result['token_id'],
                mirror_transaction_hash=result['transaction_hash']
            )
        
        return result
    
    def mint_cross_chain(self, networks=None):
        """Mintear NFT en múltiples cadenas"""
        if networks is None:
            networks = ['STARKNET_SEPOLIA', 'POLYGON_AMOY']
        
        results = {}
        for network in networks:
            if network.startswith('STARKNET'):
                results[network] = self.mint_on_starknet()
            else:
                results[network] = self.mint_on_polygon()
        
        # Marcar como cross-chain si al menos una operación fue exitosa
        if any(r['success'] for r in results.values()):
            self.multichain_data.is_cross_chain = True
            self.multichain_data.save()
        
        return results
    
    def get_multichain_info(self):
        """Obtener información del animal en todas las cadenas"""
        mirrors = self.multichain_data.mirrors.all()
        
        info = {
            'animal_id': self.animal.id,
            'ear_tag': self.animal.ear_tag,
            'primary_network': str(self.multichain_data.primary_network),
            'is_cross_chain': self.multichain_data.is_cross_chain,
            'mirrors': []
        }
        
        for mirror in mirrors:
            info['mirrors'].append({
                'network': mirror.network.name,
                'network_type': mirror.network.network_type,
                'token_id': mirror.token_id,
                'transaction_hash': mirror.mirror_transaction_hash,
                'explorer_url': self._get_explorer_url(mirror)
            })
        
        return info
    
    def _get_default_contract_address(self):
        """Obtener dirección del contrato por defecto para Starknet"""
        # Buscar contrato desplegado o usar uno por defecto
        from core.starknet.models import StarknetContract
        try:
            contract = StarknetContract.objects.filter(
                network__network_id='STARKNET_SEPOLIA',
                contract_name='AnimalNFT'
            ).first()
            return contract.address if contract else os.getenv('STARKNET_NFT_CONTRACT')
        except:
            return os.getenv('STARKNET_NFT_CONTRACT')
    
    def _get_explorer_url(self, mirror):
        """Generar URL del explorador para la transacción"""
        base_url = mirror.network.explorer_url
        if mirror.network.is_starknet:
            return f"{base_url}/tx/{mirror.mirror_transaction_hash}"
        else:
            return f"{base_url}/tx/{mirror.mirror_transaction_hash}"

# Mixin para añadir funcionalidad multichain a modelos existentes
class MultichainMixin:
    """Mixin para añadir capacidades multichain a cualquier modelo"""
    
    @property
    def multichain(self):
        """Acceder al adaptador multichain"""
        return AnimalMultichainAdapter(self)
    
    def get_multichain_status(self):
        """Estado multichain del modelo"""
        adapter = AnimalMultichainAdapter(self)
        return adapter.get_multichain_info()