from django.contrib.auth.models import AbstractUser
from django.db import models

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
    ]
    
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES,
        default='PRODUCER',
        verbose_name="Rol"
    )
    wallet_address = models.CharField(
        max_length=42, 
        unique=True,
        verbose_name="Dirección Wallet"
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name="Verificado en Blockchain"
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
        ]

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"