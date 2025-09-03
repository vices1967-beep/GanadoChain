from django.db import models
from django.conf import settings

class CattleAuditTrail(models.Model):
    """Auditoría específica para modelos de ganado"""
    ACTION_TYPES = [
        ('CREATE', 'Creación'),
        ('UPDATE', 'Actualización'),
        ('DELETE', 'Eliminación'),
        ('TRANSFER', 'Transferencia'),
        ('STATUS_CHANGE', 'Cambio de Estado'),
        ('HEALTH_UPDATE', 'Actualización de Salud'),
    ]
    
    object_type = models.CharField(max_length=100)  # 'animal', 'batch', 'health_record'
    object_id = models.CharField(max_length=100)
    action_type = models.CharField(max_length=15, choices=ACTION_TYPES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    previous_state = models.JSONField(blank=True, null=True)
    new_state = models.JSONField(blank=True, null=True)
    changes = models.JSONField()  # Campos específicos que cambiaron
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    blockchain_tx_hash = models.CharField(max_length=66, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['object_type', 'object_id']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]
        ordering = ['-timestamp']