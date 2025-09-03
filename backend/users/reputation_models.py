from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class UserRole(models.Model):
    """Roles detallados con scope granular"""
    
    # Usar la definición de choices del modelo User
    ROLE_SCOPES = [
        ('GLOBAL', 'Global'),
        ('BATCH', 'Por Lote'),
        ('ANIMAL', 'Por Animal'),
        ('LOCATION', 'Por Ubicación'),
    ]
    
    # Referenciar directamente desde el modelo User
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='detailed_roles'
    )
    
    # ✅ CORREGIDO: Usar User.BLOCKCHAIN_ROLE_CHOICES en lugar de settings
    role_type = models.CharField(
        max_length=20, 
        choices=[]  # Se establecerá en __init__ para evitar referencia circular
    )
    
    scope_type = models.CharField(
        max_length=10, 
        choices=ROLE_SCOPES, 
        default='GLOBAL'
    )
    
    scope_id = models.CharField(max_length=100, blank=True)
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='granted_roles'
    )
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['user', 'role_type', 'scope_type', 'scope_id']
        verbose_name = "Rol Detallado de Usuario"
        verbose_name_plural = "Roles Detallados de Usuario"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer las choices después de la importación para evitar circular
        from .models import User
        self._meta.get_field('role_type').choices = User.BLOCKCHAIN_ROLE_CHOICES

    def __str__(self):
        return f"{self.user.username} - {self.role_type} - {self.scope_type}"

    def clean(self):
        super().clean()
        # Validar que el scope_id sea proporcionado si no es GLOBAL
        if self.scope_type != 'GLOBAL' and not self.scope_id:
            raise ValidationError({
                'scope_id': 'Se requiere un ID de scope para alcances no globales'
            })

class ReputationScore(models.Model):
    """Sistema de reputación por tipo de usuario"""
    
    REPUTATION_TYPES = [
        ('PRODUCER', 'Productor'),
        ('VET', 'Veterinario'),
        ('FRIGORIFICO', 'Frigorífico'),
        ('AUDITOR', 'Auditor'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    
    reputation_type = models.CharField(
        max_length=15, 
        choices=REPUTATION_TYPES
    )
    
    score = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.0
    )
    
    total_actions = models.IntegerField(default=0)
    positive_actions = models.IntegerField(default=0)
    last_calculated = models.DateTimeField(auto_now=True)
    metrics = models.JSONField(default=dict)

    class Meta:
        unique_together = ['user', 'reputation_type']
        verbose_name = "Puntuación de Reputación"
        verbose_name_plural = "Puntuaciones de Reputación"

    def __str__(self):
        return f"{self.user.username} - {self.reputation_type} - {self.score}"