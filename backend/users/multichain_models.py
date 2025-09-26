# backend/users/multichain_models.py
from django.db import models
from django.contrib.auth import get_user_model
from core.multichain.models import BlockchainNetwork
from core.multichain.manager import multichain_manager
from django.utils import timezone
import secrets

class UserMultichainProfile(models.Model):
    """Perfil multichain extendido para usuarios"""
    user = models.OneToOneField(
        'users.User', 
        on_delete=models.CASCADE, 
        related_name='multichain_profile'
    )
    
    # Wallet principal (compatible con múltiples cadenas)
    primary_wallet_address = models.CharField(
        max_length=255, 
        verbose_name="Wallet Principal",
        help_text="Wallet principal para recibir pagos y NFTs"
    )
    
    # Wallets adicionales por cadena
    secondary_wallets = models.JSONField(
        default=dict,
        verbose_name="Wallets Secundarios",
        help_text="Wallets específicos por blockchain: {'STARKNET': '0x123...', 'POLYGON': '0x456...'}"
    )
    
    # Preferencias multichain
    default_network = models.ForeignKey(
        BlockchainNetwork,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Red por Defecto"
    )
    preferred_networks = models.ManyToManyField(
        BlockchainNetwork,
        related_name='preferred_by_users',
        blank=True,
        verbose_name="Redes Preferidas"
    )
    
    # Estadísticas multichain
    total_transactions = models.IntegerField(default=0, verbose_name="Total Transacciones")
    transactions_by_network = models.JSONField(
        default=dict,
        verbose_name="Transacciones por Red"
    )
    
    # Saldos en diferentes cadenas (caché)
    balance_cache = models.JSONField(
        default=dict,
        verbose_name="Saldos en Cache",
        help_text="Saldos de tokens por red: {'STARKNET': {'ETH': 1.5}, 'POLYGON': {'MATIC': 100}}"
    )
    balance_last_updated = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Última Actualización de Saldos"
    )
    
    # Configuración de seguridad
    backup_phrase_stored = models.BooleanField(
        default=False,
        verbose_name="Frase de Respaldo Almacenada"
    )
    two_factor_auth = models.BooleanField(
        default=False,
        verbose_name="Autenticación en Dos Factores"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil Multichain de Usuario"
        verbose_name_plural = "Perfiles Multichain de Usuario"

    def __str__(self):
        return f"Multichain Profile - {self.user.username}"
    
    def save(self, *args, **kwargs):
        # Si no hay wallet principal, usar la del usuario
        if not self.primary_wallet_address and self.user.wallet_address:
            self.primary_wallet_address = self.user.wallet_address
        super().save(*args, **kwargs)
    
    def get_wallet_for_network(self, network_id):
        """Obtener wallet específico para una red"""
        return self.secondary_wallets.get(network_id, self.primary_wallet_address)
    
    def add_secondary_wallet(self, network_id, wallet_address):
        """Añadir wallet secundario para una red específica"""
        self.secondary_wallets[network_id] = wallet_address
        self.save()
    
    def get_balance(self, network_id, token_symbol='NATIVE'):
        """Obtener balance de una red y token específicos"""
        network_balances = self.balance_cache.get(network_id, {})
        return network_balances.get(token_symbol, 0)
    
    def update_balance_cache(self, network_id, balances):
        """Actualizar caché de balances"""
        if network_id not in self.balance_cache:
            self.balance_cache[network_id] = {}
        
        self.balance_cache[network_id].update(balances)
        self.balance_last_updated = timezone.now()
        self.save()

class UserBlockchainRole(models.Model):
    """Roles de usuario en diferentes blockchains"""
    ROLE_TYPES = [
        ('PRODUCER', 'Productor'),
        ('VETERINARIAN', 'Veterinario'),
        ('AUDITOR', 'Auditor'),
        ('CERTIFIER', 'Certificador'),
        ('CONSUMER', 'Consumidor'),
        ('ADMIN', 'Administrador'),
    ]
    
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='user_blockchain_roles')
    network = models.ForeignKey(BlockchainNetwork, on_delete=models.CASCADE)
    role_type = models.CharField(max_length=20, choices=ROLE_TYPES)
    
    # Referencia en blockchain
    blockchain_role_id = models.CharField(max_length=100, blank=True, verbose_name="ID de Rol en Blockchain")
    granted_by = models.ForeignKey(
        'users.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='granted_blockchain_roles'
    )
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    transaction_hash = models.CharField(max_length=255, blank=True, verbose_name="Transacción de Concesión")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Rol Blockchain de Usuario"
        verbose_name_plural = "Roles Blockchain de Usuario"
        unique_together = ['user', 'network', 'role_type']
        indexes = [
            models.Index(fields=['user', 'network']),
            models.Index(fields=['role_type', 'is_active']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_role_type_display()} en {self.network.name}"
    
    @property
    def is_expired(self):
        """Verificar si el rol ha expirado"""
        from django.utils import timezone
        return self.expires_at and self.expires_at < timezone.now()

class UserTransactionHistory(models.Model):
    """Historial de transacciones de usuario por cadena"""
    TRANSACTION_TYPES = [
        ('NFT_MINT', 'Mint de NFT'),
        ('NFT_TRANSFER', 'Transferencia de NFT'),
        ('TOKEN_MINT', 'Mint de Tokens'),
        ('TOKEN_TRANSFER', 'Transferencia de Tokens'),
        ('CERTIFICATION_ISSUE', 'Emisión de Certificación'),
        ('SUBSCRIPTION_PAYMENT', 'Pago de Suscripción'),
        ('REWARD_CLAIM', 'Reclamación de Recompensa'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('CONFIRMED', 'Confirmada'),
        ('FAILED', 'Fallida'),
        ('REVERTED', 'Revertida'),
    ]
    
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='user_transactions')
    network = models.ForeignKey(BlockchainNetwork, on_delete=models.CASCADE)
    
    # Información de la transacción
    transaction_type = models.CharField(max_length=30, choices=TRANSACTION_TYPES)
    transaction_hash = models.CharField(max_length=255, verbose_name="Hash de Transacción")
    from_address = models.CharField(max_length=255, verbose_name="Dirección Origen")
    to_address = models.CharField(max_length=255, verbose_name="Dirección Destino")
    
    # Valores y tokens
    value = models.DecimalField(
        max_digits=30, 
        decimal_places=18, 
        default=0,
        verbose_name="Valor"
    )
    token_symbol = models.CharField(max_length=20, default='NATIVE', verbose_name="Símbolo del Token")
    token_address = models.CharField(max_length=255, blank=True, verbose_name="Dirección del Token")
    
    # Metadata de la transacción
    block_number = models.BigIntegerField(null=True, blank=True, verbose_name="Número de Bloque")
    gas_used = models.DecimalField(max_digits=30, decimal_places=0, null=True, blank=True, verbose_name="Gas Utilizado")
    gas_price = models.DecimalField(max_digits=30, decimal_places=0, null=True, blank=True, verbose_name="Precio del Gas")
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    error_message = models.TextField(blank=True, verbose_name="Mensaje de Error")
    
    # Relación con objetos del sistema
    related_object_type = models.CharField(max_length=50, blank=True, verbose_name="Tipo de Objeto Relacionado")
    related_object_id = models.CharField(max_length=100, blank=True, verbose_name="ID del Objeto Relacionado")
    
    timestamp = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name="Confirmada el")

    class Meta:
        verbose_name = "Historial de Transacciones"
        verbose_name_plural = "Historial de Transacciones"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['transaction_hash']),
            models.Index(fields=['network', 'status']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_transaction_type_display()} - {self.transaction_hash[:10]}..."
    
    @property
    def explorer_url(self):
        """URL del explorador de la transacción"""
        base_url = self.network.explorer_url
        if self.network.is_starknet:
            return f"{base_url}/tx/{self.transaction_hash}"
        else:
            return f"{base_url}/tx/{self.transaction_hash}"
    
    @property
    def gas_cost_eth(self):
        """Costo de gas en ETH/MATIC"""
        if self.gas_used and self.gas_price:
            return (self.gas_used * self.gas_price) / 10**18
        return None

class UserAPICredentials(models.Model):
    """Credenciales API para integración con diferentes blockchains"""
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='user_api_credentials')
    network = models.ForeignKey(BlockchainNetwork, on_delete=models.CASCADE)
    
    # Credenciales específicas por red
    api_key = models.CharField(max_length=255, blank=True, verbose_name="API Key")
    api_secret = models.CharField(max_length=255, blank=True, verbose_name="API Secret")
    access_token = models.TextField(blank=True, verbose_name="Access Token")
    refresh_token = models.TextField(blank=True, verbose_name="Refresh Token")
    
    # Configuración
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    rate_limit = models.IntegerField(default=1000, verbose_name="Límite de Tasa")
    permissions = models.JSONField(default=dict, verbose_name="Permisos API")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Expira el")
    last_used = models.DateTimeField(null=True, blank=True, verbose_name="Último Uso")

    class Meta:
        verbose_name = "Credenciales API de Usuario"
        verbose_name_plural = "Credenciales API de Usuario"
        unique_together = ['user', 'network']

    def __str__(self):
        return f"API Credentials - {self.user.username} - {self.network.name}"
    
    def encrypt_secrets(self):
        """Encriptar secretos antes de guardar (placeholder)"""
        # Implementar encriptación real
        pass
    
    def is_expired(self):
        """Verificar si las credenciales han expirado"""
        from django.utils import timezone
        return self.expires_at and self.expires_at < timezone.now()