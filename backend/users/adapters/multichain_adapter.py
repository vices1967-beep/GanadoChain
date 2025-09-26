# backend/users/adapters/multichain_adapter.py
from django.db import models
from core.multichain.manager import multichain_manager
from core.starknet.client import SyncStarknetClient
from users.multichain_models import UserMultichainProfile, UserBlockchainRole, UserTransactionHistory
import asyncio
from django.utils import timezone
import logging
# Crea un logger para este archivo
logger = logging.getLogger(__name__)

class UserMultichainAdapter:
    """Adaptador multichain para usuarios existentes - MEJORADO"""
    
    def __init__(self, user):
        self.user = user
        self.multichain_profile, _ = UserMultichainProfile.objects.get_or_create(user=user)
    
    def setup_multichain_wallets(self, networks=None):
        """Configurar wallets para múltiples cadenas - MEJORADO"""
        if networks is None:
            networks = ['STARKNET_SEPOLIA', 'POLYGON_AMOY', 'ETHEREUM_SEPOLIA']
        
        results = {}
        for network_id in networks:
            results[network_id] = self._setup_wallet_for_network(network_id)
        
        # Habilitar multichain después de configurar wallets
        self.user.multichain_enabled = True
        self.user.last_multichain_sync = timezone.now()
        self.user.save()
        
        return results
    
    def _setup_wallet_for_network(self, network_id):
        """Configurar wallet para una red específica - MEJORADO"""
        try:
            network = multichain_manager.get_network(network_id)
            
            if network.is_starknet:
                return self._setup_starknet_wallet(network)
            else:
                return self._setup_evm_wallet(network)
                
        except Exception as e:
            logger.error(f"Error setting up wallet for {network_id}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _setup_starknet_wallet(self, network):
        """Configurar wallet de Starknet - MEJORADO"""
        try:
            # Usar el cliente Starknet para generar/importar wallet
            client = SyncStarknetClient(network.rpc_url)
            
            # Si ya existe wallet secundario, usarlo
            existing_wallet = self.multichain_profile.secondary_wallets.get('STARKNET_SEPOLIA')
            if existing_wallet:
                return {
                    'success': True,
                    'wallet_address': existing_wallet,
                    'network': network.name,
                    'status': 'existing'
                }
            
            # Generar nueva wallet (en producción usaría un sistema seguro)
            starknet_address = self._generate_starknet_wallet()
            
            self.multichain_profile.add_secondary_wallet('STARKNET_SEPOLIA', starknet_address)
            self.multichain_profile.save()
            
            return {
                'success': True,
                'wallet_address': starknet_address,
                'network': network.name,
                'status': 'new'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _setup_evm_wallet(self, network):
        """Configurar wallet EVM - MEJORADO"""
        try:
            # Para EVM chains, usar la wallet principal del usuario
            evm_address = self.multichain_profile.primary_wallet_address
            
            self.multichain_profile.add_secondary_wallet(network.network_id, evm_address)
            self.multichain_profile.save()
            
            return {
                'success': True,
                'wallet_address': evm_address,
                'network': network.name,
                'status': 'existing'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _generate_starknet_wallet(self):
        """Generar dirección de Starknet (simulada)"""
        # EN PRODUCCIÓN: Usar biblioteca segura para generar wallets
        # Esto es solo para desarrollo/demo
        import hashlib
        base_address = self.multichain_profile.primary_wallet_address
        hash_obj = hashlib.sha256(base_address.encode() + b'starknet_salt').hexdigest()
        return f"0x{hash_obj[:64]}"
    
    def assign_certifier_role(self, network_id='STARKNET_SEPOLIA', granted_by=None, expires_days=365):
        """Asignar rol de certificador específico"""
        return self.assign_blockchain_role('CERTIFIER_ROLE', network_id, granted_by, expires_days)
    
    def get_certification_capabilities(self):
        """Obtener capacidades de certificación del usuario"""
        capabilities = {
            'can_issue_certifications': self.user.can_issue_certifications,
            'can_audit_certifications': self.user.can_audit_certifications,
            'multichain_enabled': self.user.multichain_enabled,
            'available_networks': [],
            'starknet_ready': False
        }
        
        if self.user.multichain_enabled and hasattr(self.user, 'multichain_profile'):
            profile = self.user.multichain_profile
            capabilities['available_networks'] = list(profile.secondary_wallets.keys())
            capabilities['starknet_ready'] = 'STARKNET_SEPOLIA' in profile.secondary_wallets
            
        return capabilities

    # Los demás métodos permanecen igual con mejoras menores...


# Mixin para añadir a tu modelo User existente
class MultichainUserMixin:
    """Mixin para añadir capacidades multichain al modelo User"""
    
    @property
    def multichain(self):
        """Acceder al adaptador multichain"""
        from users.adapters.multichain_adapter import UserMultichainAdapter
        return UserMultichainAdapter(self)
    
    def has_blockchain_role(self, role_type, network_id=None):
        """Verificar si tiene un rol específico"""
        if network_id:
            return UserBlockchainRole.objects.filter(
                user=self,
                role_type=role_type,
                network__network_id=network_id,
                is_active=True
            ).exists()
        else:
            return UserBlockchainRole.objects.filter(
                user=self,
                role_type=role_type,
                is_active=True
            ).exists()
    
    def get_multichain_info(self):
        """Obtener información multichain del usuario"""
        return self.multichain_profile.get_multichain_info() if hasattr(self, 'multichain_profile') else {}