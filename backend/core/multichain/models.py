# backend/core/multichain/models.py
from django.db import models
from django.core.exceptions import ValidationError
import json

class BlockchainNetwork(models.Model):
    """Registro de redes blockchain soportadas"""
    NETWORK_CHOICES = [
        ('POLYGON_AMOY', 'Polygon Amoy (Testnet)'),
        ('POLYGON_MAINNET', 'Polygon Mainnet'),
        ('STARKNET_SEPOLIA', 'Starknet Sepolia'),
        ('STARKNET_MAINNET', 'Starknet Mainnet'),
        ('BITCOIN', 'Bitcoin'),
        ('ETHEREUM', 'Ethereum'),
    ]
    
    NETWORK_TYPES = [
        ('EVM', 'EVM Compatible'),
        ('STARKNET', 'Starknet'),
        ('BITCOIN', 'Bitcoin'),
    ]
    
    name = models.CharField(max_length=100)
    network_id = models.CharField(max_length=50, choices=NETWORK_CHOICES, unique=True)
    network_type = models.CharField(max_length=20, choices=NETWORK_TYPES)
    chain_id = models.BigIntegerField()
    rpc_url = models.CharField(max_length=500)
    explorer_url = models.CharField(max_length=500)
    native_currency = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    is_testnet = models.BooleanField(default=True)
    priority = models.IntegerField(default=1)  # Prioridad de uso
    
    # Configuraciones específicas por red
    config = models.JSONField(default=dict)
    
    class Meta:
        verbose_name = "Red Blockchain"
        verbose_name_plural = "Redes Blockchain"
        ordering = ['priority', 'network_id']

    def __str__(self):
        return f"{self.name} ({self.network_id})"
    
    @property
    def is_evm(self):
        return self.network_type == 'EVM'
    
    @property
    def is_starknet(self):
        return self.network_type == 'STARKNET'

class SmartContractAbstract(models.Model):
    """Modelo abstracto para contratos multichain"""
    contract_name = models.CharField(max_length=100)
    contract_version = models.CharField(max_length=20, default='1.0.0')
    network = models.ForeignKey(BlockchainNetwork, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)  # Dirección/class hash
    
    # ABI/Interface (diferente por red)
    interface_definition = models.JSONField(default=dict)
    
    # Metadata
    is_active = models.BooleanField(default=True)
    deployment_block = models.BigIntegerField(default=0)
    deployment_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['network', 'address']),
            models.Index(fields=['contract_name']),
        ]

    def __str__(self):
        return f"{self.contract_name} v{self.contract_version} - {self.network.name}"

class CrossChainManager(models.Model):
    """Gestor de operaciones cross-chain"""
    operation_id = models.CharField(max_length=100, unique=True)
    source_network = models.ForeignKey(BlockchainNetwork, on_delete=models.CASCADE, related_name='source_operations')
    target_network = models.ForeignKey(BlockchainNetwork, on_delete=models.CASCADE, related_name='target_operations')
    operation_type = models.CharField(max_length=50, choices=[
        ('BRIDGE', 'Bridge de Tokens'),
        ('STATE_SYNC', 'Sincronización de Estado'),
        ('NFT_MIRROR', 'Espejo de NFT'),
        ('DATA_VERIFICATION', 'Verificación de Datos'),
    ])
    
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pendiente'),
        ('PROCESSING', 'Procesando'),
        ('COMPLETED', 'Completado'),
        ('FAILED', 'Fallido'),
    ], default='PENDING')
    
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Gestor Cross-Chain"
        verbose_name_plural = "Gestores Cross-Chain"
        ordering = ['-created_at']

class ChainSpecificModel(models.Model):
    """Modelo para datos específicos por cadena"""
    content_type = models.CharField(max_length=100)  # 'animal_nft', 'certification', etc.
    object_id = models.CharField(max_length=100)
    network = models.ForeignKey(BlockchainNetwork, on_delete=models.CASCADE)
    
    # Datos específicos de la cadena
    chain_data = models.JSONField(default=dict)
    transaction_hashes = models.JSONField(default=list)  # Hash(es) en esta cadena
    block_numbers = models.JSONField(default=list)
    
    # Sync status
    is_synced = models.BooleanField(default=False)
    last_sync = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['content_type', 'object_id', 'network']
        verbose_name = "Modelo Específico de Cadena"
        verbose_name_plural = "Modelos Específicos de Cadena"