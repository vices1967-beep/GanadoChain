from django.db import models
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.urls import reverse
import re
import json

class BlockchainEvent(models.Model):
    EVENT_TYPES = [
        ('MINT', 'NFT Minted'),
        ('TRANSFER', 'Token Transfer'),
        ('ROLE_ADD', 'Role Assigned'),
        ('ROLE_REMOVE', 'Role Removed'),
        ('HEALTH_UPDATE', 'Health Status Updated'),
        ('LOCATION_UPDATE', 'Location Updated'),
        ('BATCH_CREATED', 'Batch Created'),
        ('TOKEN_MINTED', 'Tokens Minted'),
        ('IOT_DATA', 'IoT Data Received'),
    ]
    
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    transaction_hash = models.CharField(max_length=66)
    block_number = models.BigIntegerField()
    animal = models.ForeignKey('cattle.Animal', on_delete=models.CASCADE, null=True, blank=True)
    batch = models.ForeignKey('cattle.Batch', on_delete=models.CASCADE, null=True, blank=True)
    from_address = models.CharField(max_length=42, blank=True)
    to_address = models.CharField(max_length=42, blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Evento Blockchain"
        verbose_name_plural = "Eventos Blockchain"
        indexes = [
            models.Index(fields=['transaction_hash']),
            models.Index(fields=['animal', 'event_type']),
            models.Index(fields=['block_number']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-block_number', '-created_at']

    def __str__(self):
        return f"{self.get_event_type_display()} - {self.transaction_hash[:10]}... - Block #{self.block_number}"

    def clean(self):
        super().clean()
        # Validar formato del hash de transacción
        if self.transaction_hash and not re.match(r'^(0x)?[0-9a-fA-F]{64}$', self.transaction_hash):
            raise ValidationError({
                'transaction_hash': 'Formato de hash de transacción inválido. Debe ser 64 caracteres hexadecimales.'
            })
        # Validar formato de addresses
        if self.from_address and not re.match(r'^(0x)?[0-9a-fA-F]{40}$', self.from_address):
            raise ValidationError({
                'from_address': 'Formato de dirección from inválido.'
            })
        if self.to_address and not re.match(r'^(0x)?[0-9a-fA-F]{40}$', self.to_address):
            raise ValidationError({
                'to_address': 'Formato de dirección to inválido.'
            })

    def save(self, *args, **kwargs):
        # Normalizar hashes antes de guardar
        if self.transaction_hash and not self.transaction_hash.startswith('0x'):
            self.transaction_hash = '0x' + self.transaction_hash
        if self.from_address and not self.from_address.startswith('0x'):
            self.from_address = '0x' + self.from_address
        if self.to_address and not self.to_address.startswith('0x'):
            self.to_address = '0x' + self.to_address
            
        super().save(*args, **kwargs)

    @property
    def polyscan_url(self):
        """URL para ver la transacción en PolyScan"""
        if self.transaction_hash:
            tx_hash = self.transaction_hash
            if not tx_hash.startswith('0x'):
                tx_hash = '0x' + tx_hash
            return f"https://amoy.polygonscan.com/tx/{tx_hash}"
        return None

    @property
    def short_hash(self):
        """Hash de transacción abreviado para visualización"""
        if self.transaction_hash:
            return f"{self.transaction_hash[:8]}...{self.transaction_hash[-6:]}"
        return "N/A"
    
    @property
    def metadata_prettified(self):
        """Metadata formateada para visualización"""
        return json.dumps(self.metadata, indent=2, ensure_ascii=False)
    
    def animal_link(self):
        if self.animal:
            url = reverse('admin:cattle_animal_change', args=[self.animal.id])
            return format_html('<a href="{}">{}</a>', url, self.animal.ear_tag)
        return "—"
    
    def batch_link(self):
        if self.batch:
            url = reverse('admin:cattle_batch_change', args=[self.batch.id])
            return format_html('<a href="{}">{}</a>', url, self.batch.name)
        return "—"

class ContractInteraction(models.Model):
    """Registro de interacciones con contratos inteligentes"""
    CONTRACT_TYPES = [
        ('NFT', 'Animal NFT'),
        ('TOKEN', 'Ganado Token'),
        ('REGISTRY', 'Registry'),
        ('IOT', 'IoT Manager'),
    ]
    
    ACTION_TYPES = [
        ('MINT', 'Mint'),
        ('TRANSFER', 'Transfer'),
        ('BURN', 'Burn'),
        ('UPDATE', 'Update'),
        ('ROLE_GRANT', 'Grant Role'),
        ('ROLE_REVOKE', 'Revoke Role'),
        ('APPROVE', 'Approve'),
        ('BATCH_MINT', 'Batch Mint'),
        ('HEALTH_UPDATE', 'Update Health'),
    ]
    
    contract_type = models.CharField(max_length=10, choices=CONTRACT_TYPES)
    action_type = models.CharField(max_length=15, choices=ACTION_TYPES)
    transaction_hash = models.CharField(max_length=66)
    block_number = models.BigIntegerField()
    caller_address = models.CharField(max_length=42)
    target_address = models.CharField(max_length=42, blank=True)
    parameters = models.JSONField(default=dict)
    gas_used = models.BigIntegerField(null=True, blank=True)
    gas_price = models.BigIntegerField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=[
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('PENDING', 'Pending')
    ], default='PENDING')
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Interacción con Contrato"
        verbose_name_plural = "Interacciones con Contratos"
        indexes = [
            models.Index(fields=['transaction_hash']),
            models.Index(fields=['caller_address']),
            models.Index(fields=['contract_type', 'action_type']),
            models.Index(fields=['block_number']),
        ]
        ordering = ['-block_number', '-created_at']

    def __str__(self):
        return f"{self.contract_type} - {self.action_type} - {self.short_hash}"

    def clean(self):
        super().clean()
        if self.transaction_hash and not re.match(r'^(0x)?[0-9a-fA-F]{64}$', self.transaction_hash):
            raise ValidationError({'transaction_hash': 'Hash de transacción inválido'})
        if self.caller_address and not re.match(r'^(0x)?[0-9a-fA-F]{40}$', self.caller_address):
            raise ValidationError({'caller_address': 'Dirección caller inválida'})
        if self.target_address and not re.match(r'^(0x)?[0-9a-fA-F]{40}$', self.target_address):
            raise ValidationError({'target_address': 'Dirección target inválida'})

    def save(self, *args, **kwargs):
        # Normalizar addresses
        if self.transaction_hash and not self.transaction_hash.startswith('0x'):
            self.transaction_hash = '0x' + self.transaction_hash
        if self.caller_address and not self.caller_address.startswith('0x'):
            self.caller_address = '0x' + self.caller_address
        if self.target_address and not self.target_address.startswith('0x'):
            self.target_address = '0x' + self.target_address
        super().save(*args, **kwargs)

    @property
    def short_hash(self):
        return f"{self.transaction_hash[:8]}...{self.transaction_hash[-6:]}" if self.transaction_hash else "N/A"

    @property
    def polyscan_url(self):
        if self.transaction_hash:
            return f"https://amoy.polygonscan.com/tx/{self.transaction_hash}"
        return None

    @property
    def gas_cost_eth(self):
        """Costo de gas en ETH"""
        if self.gas_used and self.gas_price:
            return (self.gas_used * self.gas_price) / 10**18
        return None
    
    @property
    def gas_cost_usd(self):
        """Costo de gas en USD (estimado)"""
        eth_price = 3000  # Precio estimado de ETH en USD
        gas_cost = self.gas_cost_eth
        if gas_cost:
            return gas_cost * eth_price
        return None
    
    @property
    def parameters_prettified(self):
        """Parámetros formateados para visualización"""
        return json.dumps(self.parameters, indent=2, ensure_ascii=False)
    
    @property
    def status_display(self):
        """Estado con colores"""
        if self.status == 'SUCCESS':
            return format_html('<span style="color: green;">✅ {}</span>', self.get_status_display())
        elif self.status == 'FAILED':
            return format_html('<span style="color: red;">❌ {}</span>', self.get_status_display())
        else:
            return format_html('<span style="color: orange;">⏳ {}</span>', self.get_status_display())

class NetworkState(models.Model):
    """Estado de la red blockchain"""
    last_block_number = models.BigIntegerField(default=0)
    last_sync_time = models.DateTimeField(auto_now=True)
    average_gas_price = models.BigIntegerField(default=0)
    active_nodes = models.IntegerField(default=0)
    chain_id = models.IntegerField(default=80002)  # Polygon Amoy
    sync_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Información adicional de la red
    network_name = models.CharField(max_length=50, default='Polygon Amoy')
    rpc_url = models.CharField(max_length=255, default='https://polygon-amoy.infura.io/v3/')
    block_time = models.FloatField(default=2.1)  # Tiempo promedio entre bloques en segundos
    native_currency = models.CharField(max_length=20, default='MATIC')
    is_testnet = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Estado de Red"
        verbose_name_plural = "Estados de Red"

    def __str__(self):
        return f"Block #{self.last_block_number} - {self.network_name}"

    @property
    def average_gas_price_gwei(self):
        """Precio promedio de gas en Gwei"""
        return self.average_gas_price / 10**9 if self.average_gas_price else 0
    
    @property
    def sync_status(self):
        """Estado de sincronización"""
        if self.sync_enabled:
            return format_html('<span style="color: green;">✅ Sincronizando</span>')
        else:
            return format_html('<span style="color: red;">❌ Detenido</span>')
    
    @property
    def last_sync_ago(self):
        """Tiempo desde la última sincronización"""
        from django.utils import timezone
        from django.utils.timesince import timesince
        if self.last_sync_time:
            return timesince(self.last_sync_time, timezone.now())
        return "Nunca"

class SmartContract(models.Model):
    """Registro de contratos inteligentes desplegados"""
    CONTRACT_TYPES = [
        ('NFT', 'Animal NFT'),
        ('TOKEN', 'Ganado Token'),
        ('REGISTRY', 'Registry'),
        ('IOT', 'IoT Manager'),
        ('BATCH', 'Batch Manager'),
    ]
    
    name = models.CharField(max_length=100)
    contract_type = models.CharField(max_length=10, choices=CONTRACT_TYPES)
    address = models.CharField(max_length=42, unique=True)
    abi = models.JSONField()
    version = models.CharField(max_length=20, default='1.0.0')
    is_active = models.BooleanField(default=True)
    deployment_block = models.BigIntegerField()
    deployment_tx_hash = models.CharField(max_length=66)
    deployer_address = models.CharField(max_length=42)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Información adicional
    implementation_address = models.CharField(max_length=42, blank=True)
    proxy_address = models.CharField(max_length=42, blank=True)
    is_upgradeable = models.BooleanField(default=False)
    admin_address = models.CharField(max_length=42, blank=True)

    class Meta:
        verbose_name = "Contrato Inteligente"
        verbose_name_plural = "Contratos Inteligentes"
        indexes = [
            models.Index(fields=['address']),
            models.Index(fields=['contract_type']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.contract_type}) - {self.short_address}"

    def clean(self):
        super().clean()
        if self.address and not re.match(r'^(0x)?[0-9a-fA-F]{40}$', self.address):
            raise ValidationError({'address': 'Dirección de contrato inválida'})
        if self.deployment_tx_hash and not re.match(r'^(0x)?[0-9a-fA-F]{64}$', self.deployment_tx_hash):
            raise ValidationError({'deployment_tx_hash': 'Hash de deployment inválido'})
        if self.deployer_address and not re.match(r'^(0x)?[0-9a-fA-F]{40}$', self.deployer_address):
            raise ValidationError({'deployer_address': 'Dirección de deployer inválida'})
        if self.implementation_address and not re.match(r'^(0x)?[0-9a-fA-F]{40}$', self.implementation_address):
            raise ValidationError({'implementation_address': 'Dirección de implementación inválida'})
        if self.proxy_address and not re.match(r'^(0x)?[0-9a-fA-F]{40}$', self.proxy_address):
            raise ValidationError({'proxy_address': 'Dirección de proxy inválida'})
        if self.admin_address and not re.match(r'^(0x)?[0-9a-fA-F]{40}$', self.admin_address):
            raise ValidationError({'admin_address': 'Dirección de admin inválida'})

    def save(self, *args, **kwargs):
        # Normalizar addresses
        addresses_to_normalize = [
            'address', 'deployment_tx_hash', 'deployer_address', 
            'implementation_address', 'proxy_address', 'admin_address'
        ]
        
        for field in addresses_to_normalize:
            value = getattr(self, field)
            if value and not value.startswith('0x'):
                setattr(self, field, '0x' + value)
                
        super().save(*args, **kwargs)

    @property
    def short_address(self):
        return f"{self.address[:8]}...{self.address[-6:]}" if self.address else "N/A"

    @property
    def polyscan_url(self):
        if self.address:
            return f"https://amoy.polygonscan.com/address/{self.address}"
        return None

    @property
    def deployment_polyscan_url(self):
        if self.deployment_tx_hash:
            return f"https://amoy.polygonscan.com/tx/{self.deployment_tx_hash}"
        return None
    
    @property
    def abi_prettified(self):
        """ABI formateada para visualización"""
        return json.dumps(self.abi, indent=2, ensure_ascii=False)
    
    @property
    def is_upgradeable_display(self):
        """Indicador visual de si es upgradeable"""
        if self.is_upgradeable:
            return format_html('<span style="color: green;">✅ Sí</span>')
        return format_html('<span style="color: red;">❌ No</span>')
    
    @property
    def is_active_display(self):
        """Indicador visual de estado activo"""
        if self.is_active:
            return format_html('<span style="color: green;">✅ Activo</span>')
        return format_html('<span style="color: red;">❌ Inactivo</span>')

class GasPriceHistory(models.Model):
    """Historial de precios de gas"""
    gas_price = models.BigIntegerField()
    gas_price_gwei = models.FloatField()
    block_number = models.BigIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Historial de Gas"
        verbose_name_plural = "Historial de Gas"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['block_number']),
        ]

    def __str__(self):
        return f"{self.gas_price_gwei} Gwei - Block #{self.block_number}"

class TransactionPool(models.Model):
    """Pool de transacciones pendientes"""
    transaction_hash = models.CharField(max_length=66, unique=True)
    raw_transaction = models.TextField()
    status = models.CharField(max_length=10, choices=[
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('CONFIRMED', 'Confirmed'),
        ('FAILED', 'Failed')
    ], default='PENDING')
    retry_count = models.IntegerField(default=0)
    last_retry = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Transacción Pendiente"
        verbose_name_plural = "Transacciones Pendientes"
        indexes = [
            models.Index(fields=['transaction_hash']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.transaction_hash[:10]}... - {self.get_status_display()}"

    def clean(self):
        super().clean()
        if self.transaction_hash and not re.match(r'^(0x)?[0-9a-fA-F]{64}$', self.transaction_hash):
            raise ValidationError({'transaction_hash': 'Hash de transacción inválido'})

    def save(self, *args, **kwargs):
        if self.transaction_hash and not self.transaction_hash.startswith('0x'):
            self.transaction_hash = '0x' + self.transaction_hash
        super().save(*args, **kwargs)
    
    @property
    def short_hash(self):
        return f"{self.transaction_hash[:8]}...{self.transaction_hash[-6:]}" if self.transaction_hash else "N/A"
    
    @property
    def polyscan_url(self):
        if self.transaction_hash:
            return f"https://amoy.polygonscan.com/tx/{self.transaction_hash}"
        return None