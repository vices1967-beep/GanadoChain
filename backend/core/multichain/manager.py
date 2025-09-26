from django.db import models
from .models import BlockchainNetwork, ChainSpecificModel

class MultichainManager:
    """Manager unificado para operaciones multichain con inicialización perezosa"""
    
    def __init__(self):
        self._networks_loaded = False
        self.networks = {}
        # NO cargar redes durante __init__
    
    def _ensure_networks_loaded(self):
        """Cargar redes solo cuando sea necesario y seguro"""
        if not self._networks_loaded:
            try:
                self._load_networks()
                self._networks_loaded = True
            except Exception as e:
                # Si la tabla no existe aún, esperar a migraciones
                print(f"Warning: No se pudieron cargar redes: {e}")
                self.networks = {}
    
    def _load_networks(self):
        """Cargar redes configuradas"""
        for network in BlockchainNetwork.objects.filter(is_active=True):
            self.networks[network.network_id] = network
    
    def get_network(self, network_id):
        """Obtener red por ID"""
        self._ensure_networks_loaded()
        return self.networks.get(network_id)
    
    def get_primary_network(self, network_type=None):
        """Obtener red principal (mayor prioridad)"""
        self._ensure_networks_loaded()
        
        # Si no hay redes cargadas, intentar consulta directa
        if not self.networks:
            try:
                networks = BlockchainNetwork.objects.filter(is_active=True)
                if network_type:
                    networks = networks.filter(network_type=network_type)
                return networks.order_by('priority').first()
            except:
                return None
        
        # Usar redes ya cargadas
        networks = list(self.networks.values())
        if network_type:
            networks = [n for n in networks if n.network_type == network_type]
        
        return sorted(networks, key=lambda x: x.priority)[0] if networks else None
    
    def deploy_contract(self, contract_name, network_id, **kwargs):
        """Desplegar contrato en una red específica"""
        network = self.get_network(network_id)
        if not network:
            raise ValueError(f"Red {network_id} no encontrada")
        
        if network.is_evm:
            return self._deploy_evm_contract(network, contract_name, **kwargs)
        elif network.is_starknet:
            return self._deploy_starknet_contract(network, contract_name, **kwargs)
        else:
            raise ValueError(f"Tipo de red no soportado: {network.network_type}")
    
    def mint_nft(self, animal, networks=None):
        """Mintear NFT en múltiples cadenas"""
        self._ensure_networks_loaded()
        
        if networks is None:
            networks = ['STARKNET_SEPOLIA', 'POLYGON_AMOY']  # Default chains
        
        results = {}
        for network_id in networks:
            try:
                if network_id.startswith('STARKNET'):
                    results[network_id] = self._mint_starknet_nft(animal, network_id)
                else:
                    results[network_id] = self._mint_evm_nft(animal, network_id)
            except Exception as e:
                results[network_id] = {'error': str(e)}
        
        return results
    
    # Métodos específicos de implementación
    def _deploy_starknet_contract(self, network, contract_name, **kwargs):
        """Desplegar contrato en Starknet"""
        from core.starknet.client import StarknetClient
        client = StarknetClient(network)
        return client.deploy_contract(contract_name, **kwargs)
    
    def _deploy_evm_contract(self, network, contract_name, **kwargs):
        """Desplegar contrato en EVM"""
        from core.evm.client import EVMClient
        client = EVMClient(network)
        return client.deploy_contract(contract_name, **kwargs)

# Singleton global con inicialización perezosa
_multichain_manager_instance = None

def get_multichain_manager():
    """Función para obtener la instancia del manager (lazy initialization)"""
    global _multichain_manager_instance
    if _multichain_manager_instance is None:
        _multichain_manager_instance = MultichainManager()
    return _multichain_manager_instance

# Alias para mantener compatibilidad
multichain_manager = get_multichain_manager()