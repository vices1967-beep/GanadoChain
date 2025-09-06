from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.html import format_html
import re
import json

# ✅ Importar validadores centralizados
from core.models import validate_ethereum_address, validate_transaction_hash, validate_ipfs_hash

User = get_user_model()

class HealthStatus(models.TextChoices):
    HEALTHY = 'HEALTHY', 'Sano'
    SICK = 'SICK', 'Enfermo'
    RECOVERING = 'RECOVERING', 'Recuperándose'
    UNDER_OBSERVATION = 'UNDER_OBSERVATION', 'En Observación'
    QUARANTINED = 'QUARANTINED', 'En Cuarentena'

class Animal(models.Model):
    ear_tag = models.CharField(max_length=100, unique=True, verbose_name="Arete")
    breed = models.CharField(max_length=100, verbose_name="Raza")
    birth_date = models.DateField(verbose_name="Fecha de Nacimiento")
    weight = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Peso (kg)")
    health_status = models.CharField(
        max_length=20, 
        choices=HealthStatus.choices,
        default=HealthStatus.HEALTHY,
        verbose_name="Estado de Salud"
    )
    location = models.CharField(max_length=255, verbose_name="Ubicación")
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='animals',
        verbose_name="Dueño"
    )
    
    # ✅ CAMPOS BLOCKCHAIN CON VALIDADORES
    ipfs_hash = models.CharField(max_length=255, blank=True, verbose_name="Hash IPFS", 
                               validators=[validate_ipfs_hash])
    token_id = models.BigIntegerField(null=True, blank=True, unique=True, verbose_name="Token ID NFT")
    mint_transaction_hash = models.CharField(max_length=66, blank=True, verbose_name="Transacción de Mint",
                                           validators=[validate_transaction_hash])
    nft_owner_wallet = models.CharField(max_length=42, blank=True, verbose_name="Wallet Owner NFT",
                                      validators=[validate_ethereum_address])
    
    # ✅ NUEVO CAMPO AÑADIDO - Relación con lote actual
    current_batch = models.ForeignKey('Batch', on_delete=models.SET_NULL, 
                                    null=True, blank=True, related_name='current_animals',
                                    verbose_name="Lote Actual")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Animal"
        verbose_name_plural = "Animales"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ear_tag']),
            models.Index(fields=['owner']),
            models.Index(fields=['health_status']),
            models.Index(fields=['token_id']),
            # ✅ NUEVOS ÍNDICES AÑADIDOS
            models.Index(fields=['health_status', 'owner']),
            models.Index(fields=['nft_owner_wallet', 'token_id']),
            models.Index(fields=['current_batch']),
        ]

    def __str__(self):
        return f"{self.ear_tag} - {self.breed}"
    
    def clean(self):
        super().clean()
        # ✅ Las validaciones ahora se manejan con los validadores centralizados
        # Se mantiene clean() por si hay otras validaciones específicas del modelo
    
    def save(self, *args, **kwargs):
        # Normalizar hashes antes de guardar
        if self.mint_transaction_hash and not self.mint_transaction_hash.startswith('0x'):
            self.mint_transaction_hash = '0x' + self.mint_transaction_hash
        if self.nft_owner_wallet and not self.nft_owner_wallet.startswith('0x'):
            self.nft_owner_wallet = '0x' + self.nft_owner_wallet
        super().save(*args, **kwargs)
    
    @property
    def is_minted(self):
        return bool(self.token_id and self.mint_transaction_hash)
    
    @property
    def metadata_uri(self):
        if self.ipfs_hash:
            return f"ipfs://{self.ipfs_hash}"
        return ""
    
    @property
    def polyscan_url(self):
        if self.mint_transaction_hash:
            tx_hash = self.mint_transaction_hash
            if not tx_hash.startswith('0x'):
                tx_hash = '0x' + tx_hash
            return f"https://amoy.polygonscan.com/tx/{tx_hash}"
        return None
    
    def polyscan_link(self):
        if self.polyscan_url:
            return format_html('<a href="{}" target="_blank">🔗 Ver en PolyScan</a>', self.polyscan_url)
        return "No disponible"
    
    def get_absolute_url(self):
        return reverse('admin:cattle_animal_change', args=[self.id])
    
    # ✅ NUEVO MÉTODO AÑADIDO - Para manejar cambios de lote
    def update_current_batch(self, new_batch):
        """
        Actualiza el lote actual del animal y maneja la lógica de transición
        """
        from cattle.signals import animal_batch_changed  # Importar aquí para evitar circular imports
        
        old_batch = self.current_batch
        self.current_batch = new_batch
        self.save()
        
        # Disparar señal para manejar lógica adicional
        animal_batch_changed.send(
            sender=self.__class__,
            animal=self,
            old_batch=old_batch,
            new_batch=new_batch
        )

class AnimalHealthRecord(models.Model):
    RECORD_SOURCE = [
        ('VETERINARIAN', 'Veterinario'),
        ('IOT_SENSOR', 'Sensor IoT'),
        ('FARMER', 'Granjero'),
        ('SYSTEM', 'Sistema Automático'),
    ]
    
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='health_records')
    health_status = models.CharField(max_length=20, choices=HealthStatus.choices)
    source = models.CharField(max_length=20, choices=RECORD_SOURCE, default='VETERINARIAN')
    veterinarian = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    iot_device_id = models.CharField(max_length=100, blank=True, verbose_name="ID Dispositivo IoT")
    notes = models.TextField(blank=True)
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Temperatura (°C)")
    heart_rate = models.IntegerField(null=True, blank=True, verbose_name="Ritmo Cardíaco (bpm)")
    movement_activity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Actividad de Movimiento")
    
    # ✅ CAMPOS BLOCKCHAIN CON VALIDADORES
    ipfs_hash = models.CharField(max_length=100, blank=True, verbose_name="Hash IPFS",
                               validators=[validate_ipfs_hash])
    transaction_hash = models.CharField(max_length=66, blank=True, verbose_name="Hash de Transacción",
                                      validators=[validate_transaction_hash])
    blockchain_hash = models.CharField(max_length=66, blank=True, null=True, verbose_name="Hash Blockchain",
                                     validators=[validate_transaction_hash])
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Registro de Salud"
        verbose_name_plural = "Registros de Salud"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['animal', 'created_at']),
            models.Index(fields=['health_status']),
            models.Index(fields=['iot_device_id']),
        ]

    def __str__(self):
        return f"{self.animal.ear_tag} - {self.get_health_status_display()} - {self.created_at}"
    
    def clean(self):
        super().clean()
        # ✅ Las validaciones ahora se manejan con los validadores centralizados
    
    def save(self, *args, **kwargs):
        # Normalizar hashes antes de guardar
        if self.transaction_hash and not self.transaction_hash.startswith('0x'):
            self.transaction_hash = '0x' + self.transaction_hash
        if self.blockchain_hash and not self.blockchain_hash.startswith('0x'):
            self.blockchain_hash = '0x' + self.blockchain_hash
        super().save(*args, **kwargs)
    
    @property
    def blockchain_linked(self):
        return bool(self.blockchain_hash)
    
    @property
    def polyscan_url(self):
        if self.transaction_hash:
            tx_hash = self.transaction_hash
            if not tx_hash.startswith('0x'):
                tx_hash = '0x' + tx_hash
            return f"https://amoy.polygonscan.com/tx/{tx_hash}"
        return None
    
    def polyscan_link(self):
        if self.polyscan_url:
            return format_html('<a href="{}" target="_blank">🔗 Ver en PolyScan</a>', self.polyscan_url)
        return "No disponible"

class Batch(models.Model):
    BATCH_STATUS_CHOICES = [
        ('CREATED', 'Creado'),
        ('IN_TRANSIT', 'En Tránsito'),
        ('DELIVERED', 'Entregado'),
        ('CANCELLED', 'Cancelado'),
        ('PROCESSING', 'Procesando'),
        ('QUALITY_CHECK', 'Control de Calidad'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nombre del Lote")
    animals = models.ManyToManyField(Animal, related_name='batches', verbose_name="Animales")
    origin = models.CharField(max_length=255, verbose_name="Origen")
    destination = models.CharField(max_length=255, verbose_name="Destino")
    status = models.CharField(
        max_length=20,
        choices=BATCH_STATUS_CHOICES,
        default='CREATED',
        verbose_name="Estado"
    )
    
    # ✅ CAMPOS BLOCKCHAIN CON VALIDADORES
    ipfs_hash = models.CharField(max_length=255, blank=True, verbose_name="Hash IPFS",
                               validators=[validate_ipfs_hash])
    blockchain_tx = models.CharField(max_length=66, blank=True, verbose_name="Transacción Blockchain",
                                   validators=[validate_transaction_hash])
    
    # ✅ NUEVO CAMPO RECOMENDADO
    on_blockchain = models.BooleanField(default=False, verbose_name="En Blockchain")
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_batches',
        verbose_name="Creado por"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Lote"
        verbose_name_plural = "Lotes"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_by']),
            models.Index(fields=['on_blockchain']),  # ← Nuevo índice
        ]

    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"
    
    # ✅ PROPIEDADES PARA COMPATIBILIDAD CON ADMIN Y SERIALIZERS
    @property
    def minted_animals_count(self):
        """Retorna el número de animales con NFT en el lote"""
        return self.animals.filter(token_id__isnull=False).count()
    
    @property
    def total_animals_count(self):
        """Retorna el número total de animales en el lote"""
        return self.animals.count()
    
    @property
    def is_minted(self):
        """Compatibilidad con propiedad existente (para consistencia)"""
        return bool(self.blockchain_tx)
    
    @property
    def metadata_uri(self):
        """Compatibilidad con propiedad existente"""
        if self.ipfs_hash:
            return f"ipfs://{self.ipfs_hash}"
        return ""
    
    def clean(self):
        super().clean()
        # ✅ Las validaciones ahora se manejan con los validadores centralizados
    
    def save(self, *args, **kwargs):
        # Normalizar hash de transacción antes de guardar
        if self.blockchain_tx and not self.blockchain_tx.startswith('0x'):
            self.blockchain_tx = '0x' + self.blockchain_tx
        
        # Actualizar automáticamente el estado on_blockchain
        self.on_blockchain = bool(self.blockchain_tx)
        
        super().save(*args, **kwargs)
    
    @property
    def polyscan_url(self):
        """URL para ver la transacción en PolyScan"""
        if self.blockchain_tx:
            tx_hash = self.blockchain_tx
            if not tx_hash.startswith('0x'):
                tx_hash = '0x' + tx_hash
            return f"https://amoy.polygonscan.com/tx/{tx_hash}"
        return None
    
    def polyscan_link(self):
        """Enlace HTML para PolyScan"""
        if self.polyscan_url:
            return format_html('<a href="{}" target="_blank">🔗 Ver en PolyScan</a>', self.polyscan_url)
        return "No disponible"
    
    def get_absolute_url(self):
        return reverse('admin:cattle_batch_change', args=[self.id])
    
    # ✅ MÉTODOS ADICIONALES PARA FUNCIONALIDAD
    def add_animal(self, animal):
        """Agrega un animal al lote"""
        if animal not in self.animals.all():
            self.animals.add(animal)
            # Actualizar el lote actual del animal
            animal.update_current_batch(self)
    
    def remove_animal(self, animal):
        """Remueve un animal del lote"""
        if animal in self.animals.all():
            self.animals.remove(animal)
            # Quitar el lote actual del animal
            animal.update_current_batch(None)
    
    def can_be_minted(self):
        """Verifica si el lote puede ser minteado"""
        if self.blockchain_tx:
            return False  # Ya está minteado
        
        # Verificar que todos los animales tengan dueño y estén sanos
        animals = self.animals.all()
        if not animals.exists():
            return False
        
        # Todos los animales deben tener el mismo dueño
        owners = set(animal.owner_id for animal in animals)
        if len(owners) > 1:
            return False
        
        # Todos los animales deben estar sanos o en observación
        invalid_statuses = [HealthStatus.SICK, HealthStatus.QUARANTINED]
        if animals.filter(health_status__in=invalid_statuses).exists():
            return False
        
        return True
    
    def get_owner(self):
        """Obtiene el dueño principal del lote (primer animal)"""
        first_animal = self.animals.first()
        return first_animal.owner if first_animal else None
    
    def update_status(self, new_status, user=None):
        """Actualiza el estado del lote con registro de auditoría"""
        old_status = self.status
        self.status = new_status
        self.save()
        
        # Registrar cambio de estado en auditoría
        if user:
            from cattle.audit_models import CattleAuditTrail
            CattleAuditTrail.objects.create(
                object_type='batch',
                object_id=self.id,
                action_type='STATUS_CHANGE',
                user=user,
                previous_state={'status': old_status},
                new_state={'status': new_status},
                changes=f'Estado cambiado de {old_status} a {new_status}'
            )