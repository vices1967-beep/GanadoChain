from django.db import models
from django.conf import settings

class Notification(models.Model):
    """Sistema de notificaciones para usuarios"""
    NOTIFICATION_TYPES = [
        ('HEALTH_ALERT', 'Alerta de Salud'),
        ('BLOCKCHAIN_TX', 'Transacción Blockchain'),
        ('IOT_ALERT', 'Alerta IoT'),
        ('BATCH_UPDATE', 'Actualización de Lote'),
        ('ROLE_CHANGE', 'Cambio de Rol'),
        ('REPUTATION_UPDATE', 'Actualización de Reputación'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    related_object_id = models.CharField(max_length=100, blank=True)
    related_content_type = models.CharField(max_length=100, blank=True)
    is_read = models.BooleanField(default=False)
    priority = models.CharField(max_length=10, choices=[
        ('LOW', 'Baja'),
        ('MEDIUM', 'Media'),
        ('HIGH', 'Alta'),
        ('URGENT', 'Urgente')
    ], default='MEDIUM')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']