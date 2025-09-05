from django.db import models
from .models import Animal, Batch

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