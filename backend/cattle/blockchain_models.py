from django.db import models
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from core.models import validate_transaction_hash

User = get_user_model()

class BlockchainEventState(models.Model):
    """Estado extendido de eventos blockchain"""
    EVENT_STATES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('FAILED', 'Failed'),
        ('REVERTED', 'Reverted'),
    ]
    
    event = models.OneToOneField('blockchain.BlockchainEvent', on_delete=models.CASCADE)
    state = models.CharField(max_length=10, choices=EVENT_STATES, default='PENDING')
    confirmation_blocks = models.IntegerField(default=0)
    block_confirmed = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Estado de Evento Blockchain"
        verbose_name_plural = "Estados de Eventos Blockchain"
    
    def __str__(self):
        return f"{self.event} - {self.state}"
    
    @property
    def is_confirmed(self):
        return self.state == 'CONFIRMED'
    
    @property
    def polyscan_url(self):
        """URL para ver la transacción en PolyScan"""
        if hasattr(self.event, 'transaction_hash') and self.event.transaction_hash:
            tx_hash = self.event.transaction_hash
            if not tx_hash.startswith('0x'):
                tx_hash = '0x' + tx_hash
            return f"https://amoy.polygonscan.com/tx/{tx_hash}"
        return None
    
    def polyscan_link(self):
        """Enlace HTML para PolyScan"""
        if self.polyscan_url:
            return format_html('<a href="{}" target="_blank">🔗 Ver en PolyScan</a>', self.polyscan_url)
        return "No disponible"

class CertificationStandard(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    issuing_authority = models.CharField(max_length=200)
    validity_days = models.IntegerField()
    requirements = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cattle_certification_standard'
        verbose_name = "Estándar de Certificación"
        verbose_name_plural = "Estándares de Certificación"

    def __str__(self):
        return self.name
    
    @property
    def polyscan_url(self):
        """URL para ver la transacción en PolyScan"""
        # Este modelo probablemente no tiene transacciones blockchain directas
        return None
    
    def polyscan_link(self):
        """Enlace HTML para PolyScan"""
        return "No aplica"

class AnimalCertification(models.Model):
    animal = models.ForeignKey('cattle.Animal', on_delete=models.CASCADE, related_name='certifications')
    standard = models.ForeignKey(CertificationStandard, on_delete=models.CASCADE)
    certification_date = models.DateTimeField()
    expiration_date = models.DateTimeField()
    certifying_authority = models.ForeignKey('users.User', on_delete=models.CASCADE, 
                                          limit_choices_to={'role': 'auditor'})
    evidence = models.JSONField(default=dict)
    blockchain_hash = models.CharField(max_length=255, blank=True, validators=[validate_transaction_hash])
    revoked = models.BooleanField(default=False)
    revocation_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cattle_animal_certification'
        verbose_name = "Certificación de Animal"
        verbose_name_plural = "Certificaciones de Animales"
        indexes = [
            models.Index(fields=['animal', 'expiration_date']),
            models.Index(fields=['certifying_authority', 'certification_date']),
        ]

    def __str__(self):
        return f"Certificación - {self.animal.ear_tag} - {self.standard.name}"
    
    def save(self, *args, **kwargs):
        # Normalizar hash antes de guardar
        if self.blockchain_hash and not self.blockchain_hash.startswith('0x'):
            self.blockchain_hash = '0x' + self.blockchain_hash
        super().save(*args, **kwargs)
    
    @property
    def polyscan_url(self):
        """URL para ver la transacción en PolyScan"""
        if self.blockchain_hash:
            tx_hash = self.blockchain_hash
            if not tx_hash.startswith('0x'):
                tx_hash = '0x' + tx_hash
            return f"https://amoy.polygonscan.com/tx/{tx_hash}"
        return None
    
    def polyscan_link(self):
        """Enlace HTML para PolyScan"""
        if self.polyscan_url:
            return format_html('<a href="{}" target="_blank">🔗 Ver en PolyScan</a>', self.polyscan_url)
        return "No disponible"