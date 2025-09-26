# backend/users/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .multichain_models import UserMultichainProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_multichain_profile(sender, instance, created, **kwargs):
    """Crear perfil multichain automáticamente para nuevos usuarios"""
    if created and instance.wallet_address:
        UserMultichainProfile.objects.create(
            user=instance,
            primary_wallet_address=instance.wallet_address
        )

@receiver(pre_save, sender=User)
def update_multichain_profile(sender, instance, **kwargs):
    """Actualizar perfil multichain cuando cambia la wallet"""
    if instance.pk and hasattr(instance, 'multichain_profile'):
        original = User.objects.get(pk=instance.pk)
        if original.wallet_address != instance.wallet_address:
            instance.multichain_profile.primary_wallet_address = instance.wallet_address
            instance.multichain_profile.save()