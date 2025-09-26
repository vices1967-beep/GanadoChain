# backend/consumer/models.py
from django.db import models
from core.multichain.manager import multichain_manager

class ConsumerTier(models.Model):
    """Niveles de acceso para consumidores con precios multichain"""
    TIER_CHOICES = [
        ('BASIC', 'Básico (Gratuito)'),
        ('PREMIUM', 'Premium'),
        ('EXPERT', 'Experto'),
        ('ENTERPRISE', 'Empresarial'),
    ]
    
    name = models.CharField(max_length=20, choices=TIER_CHOICES, unique=True)
    description = models.TextField(verbose_name="Descripción")
    monthly_fee_usd = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Tarifa Mensual (USD)")
    
    # Precios en diferentes criptomonedas (multichain)
    pricing_multichain = models.JSONField(
        default=dict,
        verbose_name="Precios Multichain",
        help_text="Precios en diferentes criptomonedas: {'MATIC': 5.0, 'ETH': 0.002}"
    )
    
    # Datos accesibles por nivel
    accessible_data = models.JSONField(
        default=list,
        verbose_name="Datos Accesibles",
        help_text="Lista de categorías de datos accesibles"
    )
    
    # Límites
    max_queries_per_month = models.IntegerField(default=100, verbose_name="Máximo de Consultas/Mes")
    can_access_premium_certs = models.BooleanField(default=False, verbose_name="Acceso a Certificaciones Premium")
    can_export_data = models.BooleanField(default=False, verbose_name="Puede Exportar Datos")
    
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Nivel de Consumidor"
        verbose_name_plural = "Niveles de Consumidor"
        ordering = ['monthly_fee_usd']

    def __str__(self):
        return f"{self.get_name_display()} - ${self.monthly_fee_usd}/mes"
    
    def get_price_in_crypto(self, cryptocurrency):
        """Obtener precio en criptomoneda específica"""
        return self.pricing_multichain.get(cryptocurrency)

class ConsumerProfile(models.Model):
    """Perfil extendido para consumidores"""
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='consumer_profile')
    tier = models.ForeignKey(ConsumerTier, on_delete=models.PROTECT, related_name='consumers')
    
    # Preferencias de pago multichain
    preferred_payment_network = models.ForeignKey(
        'core.BlockchainNetwork', 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="Red de Pago Preferida"
    )
    preferred_cryptocurrency = models.CharField(max_length=20, default='MATIC', verbose_name="Criptomoneda Preferida")
    
    # Estadísticas de uso
    total_queries = models.IntegerField(default=0, verbose_name="Total de Consultas")
    queries_this_month = models.IntegerField(default=0, verbose_name="Consultas Este Mes")
    last_query_date = models.DateTimeField(null=True, blank=True, verbose_name="Última Consulta")
    
    # Suscripción
    subscription_active = models.BooleanField(default=False, verbose_name="Suscripción Activa")
    subscription_start_date = models.DateTimeField(null=True, blank=True, verbose_name="Inicio de Suscripción")
    subscription_end_date = models.DateTimeField(null=True, blank=True, verbose_name="Fin de Suscripción")
    
    # Datos de facturación (opcional, para empresas)
    company_name = models.CharField(max_length=200, blank=True, verbose_name="Nombre de Empresa")
    vat_number = models.CharField(max_length=50, blank=True, verbose_name="NIF/CIF")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil de Consumidor"
        verbose_name_plural = "Perfiles de Consumidor"

    def __str__(self):
        return f"Consumidor: {self.user.username} - {self.tier.name}"
    
    @property
    def can_make_query(self):
        """Verificar si puede hacer consultas"""
        if not self.subscription_active:
            return False
        return self.queries_this_month < self.tier.max_queries_per_month
    
    @property
    def queries_remaining(self):
        """Consultas restantes este mes"""
        return max(0, self.tier.max_queries_per_month - self.queries_this_month)

class QRCodeAccess(models.Model):
    """Gestión de códigos QR para acceso a información"""
    qr_code = models.CharField(max_length=100, unique=True, verbose_name="Código QR")
    animal = models.ForeignKey('cattle.Animal', on_delete=models.CASCADE, verbose_name="Animal")
    cut_of_meat = models.CharField(max_length=100, blank=True, verbose_name="Corte de Carne")
    
    # Datos públicos (visibles para todos)
    public_data = models.JSONField(
        default=dict,
        verbose_name="Datos Públicos",
        help_text="Información básica visible sin autenticación"
    )
    
    # Datos premium (requieren suscripción)
    premium_data = models.JSONField(
        default=dict,
        verbose_name="Datos Premium", 
        help_text="Información detallada para suscriptores"
    )
    
    # Datos expert (máximo nivel)
    expert_data = models.JSONField(
        default=dict,
        verbose_name="Datos Experto",
        help_text="Información técnica avanzada"
    )
    
    # Certificaciones asociadas
    certifications = models.ManyToManyField('certification.Certification', blank=True, verbose_name="Certificaciones")
    
    # Metadata blockchain
    ipfs_hash = models.CharField(max_length=255, blank=True, verbose_name="Hash IPFS")
    blockchain_verified = models.BooleanField(default=False, verbose_name="Verificado en Blockchain")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Acceso por QR Code"
        verbose_name_plural = "Accesos por QR Code"
        indexes = [
            models.Index(fields=['qr_code']),
            models.Index(fields=['animal']),
        ]

    def __str__(self):
        return f"QR {self.qr_code} - {self.animal.ear_tag}"
    
    def get_data_for_tier(self, tier_name):
        """Obtener datos según el nivel del consumidor"""
        if tier_name == 'EXPERT':
            return {**self.public_data, **self.premium_data, **self.expert_data}
        elif tier_name == 'PREMIUM':
            return {**self.public_data, **self.premium_data}
        else:  # BASIC
            return self.public_data

class ConsumerAccessLog(models.Model):
    """Registro de accesos de consumidores"""
    consumer = models.ForeignKey('users.User', on_delete=models.CASCADE)
    animal = models.ForeignKey('cattle.Animal', on_delete=models.CASCADE)
    access_tier = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)

