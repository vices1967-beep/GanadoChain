# ✅ Importar validadores centralizados
from core.models import validate_ethereum_address, validate_transaction_hash

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.html import format_html
import re

class User(AbstractUser):
    ROLE_CHOICES = [
        ('PRODUCER', 'Productor'),
        ('VET', 'Veterinario'),
        ('FRIGORIFICO', 'Frigorífico'),
        ('AUDITOR', 'Auditor'),
        ('IOT', 'Dispositivo IoT'),
        ('ADMIN', 'Administrador'),
        ('DAO', 'Miembro DAO'),
        ('CONSUMER', 'Consumidor'),
        ('VIEWER', 'Solo Lectura'),
    ]
    
    BLOCKCHAIN_ROLE_CHOICES = [
        ('PRODUCER_ROLE', 'Productor'),
        ('VET_ROLE', 'Veterinario'),
        ('FRIGORIFICO_ROLE', 'Frigorífico'),
        ('AUDITOR_ROLE', 'Auditor'),
        ('IOT_ROLE', 'Dispositivo IoT'),
        ('DAO_ROLE', 'Miembro DAO'),
        ('DEFAULT_ADMIN_ROLE', 'Administrador'),
    ]
    
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES,
        default='PRODUCER',
        verbose_name="Rol de Sistema"
    )
    wallet_address = models.CharField(
        max_length=42, 
        unique=True,
        verbose_name="Dirección Wallet",
        validators=[validate_ethereum_address]  # ✅ VALIDADOR AÑADIDO
    )
    blockchain_roles = models.JSONField(
        default=list,
        verbose_name="Roles en Blockchain",
        help_text="Roles asignados en los contratos inteligentes"
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name="Verificado en Blockchain"
    )
    verification_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Verificación"
    )
    profile_image = models.ImageField(
        upload_to='profiles/',
        null=True,
        blank=True,
        verbose_name="Imagen de Perfil"
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Teléfono"
    )
    company = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Empresa/Organización"
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Ubicación"
    )
    bio = models.TextField(
        blank=True,
        verbose_name="Biografía"
    )
    website = models.URLField(
        blank=True,
        verbose_name="Sitio Web"
    )
    twitter_handle = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Twitter"
    )
    discord_handle = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Discord"
    )
    is_blockchain_active = models.BooleanField(
        default=True,
        verbose_name="Activo en Blockchain"
    )
    last_blockchain_sync = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Última Sincronización Blockchain"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        indexes = [
            models.Index(fields=['wallet_address']),
            models.Index(fields=['role']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['is_blockchain_active']),
            models.Index(fields=['company']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.username} - {self.get_role_display()} ({self.wallet_short})"
    
    def clean(self):
        super().clean()
        
        # ✅ La validación de wallet_address ahora se maneja con el validador centralizado
        
        # Validar que el email sea único si se proporciona
        if self.email and User.objects.filter(email=self.email).exclude(id=self.id).exists():
            raise ValidationError({
                'email': 'Este correo electrónico ya está registrado.'
            })
    
    def save(self, *args, **kwargs):
        # Normalizar wallet address
        if self.wallet_address and not self.wallet_address.startswith('0x'):
            self.wallet_address = '0x' + self.wallet_address.lower()
        
        # Normalizar email
        if self.email:
            self.email = self.email.lower()
        
        super().save(*args, **kwargs)
    
    @property
    def wallet_short(self):
        """Dirección wallet abreviada para visualización"""
        if self.wallet_address:
            return f"{self.wallet_address[:6]}...{self.wallet_address[-4:]}"
        return "N/A"
    
    @property
    def has_blockchain_roles(self):
        """Verificar si tiene roles asignados en blockchain"""
        return bool(self.blockchain_roles)
    
    @property
    def primary_blockchain_role(self):
        """Obtener el rol principal de blockchain"""
        if self.blockchain_roles:
            return self.blockchain_roles[0]
        return None
    
    @property
    def is_producer(self):
        return self.role == 'PRODUCER' or 'PRODUCER_ROLE' in self.blockchain_roles
    
    @property
    def is_veterinarian(self):
        return self.role == 'VET' or 'VET_ROLE' in self.blockchain_roles
    
    @property
    def is_auditor(self):
        return self.role == 'AUDITOR' or 'AUDITOR_ROLE' in self.blockchain_roles
    
    @property
    def can_mint_tokens(self):
        """Verificar si puede mintear tokens"""
        return self.is_producer or self.is_veterinarian or self.is_superuser
    
    @property
    def can_verify_animals(self):
        """Verificar si puede verificar animales"""
        return self.is_veterinarian or self.is_auditor or self.is_superuser
    
    @property
    def can_manage_users(self):
        """Verificar si puede gestionar usuarios"""
        return self.role in ['ADMIN', 'AUDITOR'] or self.is_superuser
    
    @property
    def profile_completion(self):
        """Calcular porcentaje de completitud del perfil"""
        fields_to_check = [
            'first_name', 'last_name', 'email', 'phone_number',
            'company', 'location', 'bio', 'profile_image'
        ]
        
        completed = 0
        for field in fields_to_check:
            if getattr(self, field):
                completed += 1
        
        return (completed / len(fields_to_check)) * 100
    
    def get_absolute_url(self):
        return reverse('admin:users_user_change', args=[self.id])
    
    def add_blockchain_role(self, role):
        """Añadir un rol de blockchain"""
        if role not in self.blockchain_roles:
            self.blockchain_roles.append(role)
            self.save()
    
    def remove_blockchain_role(self, role):
        """Remover un rol de blockchain"""
        if role in self.blockchain_roles:
            self.blockchain_roles.remove(role)
            self.save()
    
    def has_blockchain_role(self, role):
        """Verificar si tiene un rol específico en blockchain"""
        return role in self.blockchain_roles

class UserActivityLog(models.Model):
    """Registro de actividad de usuarios"""
    ACTION_CHOICES = [
        ('LOGIN', 'Inicio de Sesión'),
        ('LOGOUT', 'Cierre de Sesión'),
        ('NFT_MINT', 'Mint de NFT'),
        ('TOKEN_MINT', 'Mint de Tokens'),
        ('HEALTH_UPDATE', 'Actualización de Salud'),
        ('ROLE_ASSIGN', 'Asignación de Rol'),
        ('PROFILE_UPDATE', 'Actualización de Perfil'),
        ('PASSWORD_CHANGE', 'Cambio de Contraseña'),
        ('BLOCKCHAIN_INTERACTION', 'Interacción con Blockchain'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activity_logs',
        verbose_name="Usuario"
    )
    action = models.CharField(
        max_length=30,
        choices=ACTION_CHOICES,
        verbose_name="Acción"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Dirección IP"
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name="User Agent"
    )
    metadata = models.JSONField(
        default=dict,
        verbose_name="Metadatos"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Timestamp"
    )
    blockchain_tx_hash = models.CharField(
        max_length=66,
        blank=True,
        verbose_name="Hash de Transacción",
        validators=[validate_transaction_hash]  # ✅ VALIDADOR AÑADIDO
    )

    class Meta:
        verbose_name = "Registro de Actividad"
        verbose_name_plural = "Registros de Actividad"
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action']),
            models.Index(fields=['timestamp']),
        ]
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} - {self.timestamp}"
    
    @property
    def short_tx_hash(self):
        if self.blockchain_tx_hash:
            return f"{self.blockchain_tx_hash[:8]}...{self.blockchain_tx_hash[-6:]}"
        return "N/A"
    
    def save(self, *args, **kwargs):
        # Normalizar hash antes de guardar
        if self.blockchain_tx_hash and not self.blockchain_tx_hash.startswith('0x'):
            self.blockchain_tx_hash = '0x' + self.blockchain_tx_hash
        super().save(*args, **kwargs)

class UserPreference(models.Model):
    """Preferencias de usuario"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='preferences',
        verbose_name="Usuario"
    )
    email_notifications = models.BooleanField(
        default=True,
        verbose_name="Notificaciones por Email"
    )
    push_notifications = models.BooleanField(
        default=True,
        verbose_name="Notificaciones Push"
    )
    language = models.CharField(
        max_length=10,
        default='es',
        choices=[('es', 'Español'), ('en', 'English')],
        verbose_name="Idioma"
    )
    theme = models.CharField(
        max_length=20,
        default='light',
        choices=[('light', 'Claro'), ('dark', 'Oscuro'), ('auto', 'Automático')],
        verbose_name="Tema"
    )
    animals_per_page = models.IntegerField(
        default=20,
        verbose_name="Animales por Página"
    )
    enable_animations = models.BooleanField(
        default=True,
        verbose_name="Habilitar Animaciones"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Preferencia de Usuario"
        verbose_name_plural = "Preferencias de Usuario"
        ordering = ['-updated_at']  # AÑADIR ESTO

    def __str__(self):
        return f"Preferencias de {self.user.username}"

class APIToken(models.Model):
    """Tokens de API para integraciones"""
    TOKEN_TYPES = [
        ('READ', 'Solo Lectura'),
        ('WRITE', 'Lectura y Escritura'),
        ('ADMIN', 'Administración'),
        ('IOT', 'Dispositivo IoT'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='api_tokens',
        verbose_name="Usuario"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Nombre del Token"
    )
    token = models.CharField(
        max_length=64,
        unique=True,
        verbose_name="Token"
    )
    token_type = models.CharField(
        max_length=10,
        choices=TOKEN_TYPES,
        default='READ',
        verbose_name="Tipo de Token"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Expira el"
    )
    last_used = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Último Uso"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Token de API"
        verbose_name_plural = "Tokens de API"
        ordering = ['-created_at']  # AÑADIR ESTO
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
    @property
    def is_expired(self):
        from django.utils import timezone
        return self.expires_at and self.expires_at < timezone.now()