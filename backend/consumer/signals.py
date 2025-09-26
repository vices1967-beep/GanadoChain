# backend/consumer/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import ConsumerProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_consumer_profile(sender, instance, created, **kwargs):
    """Crear perfil de consumidor automáticamente para usuarios con rol CONSUMER"""
    if created and instance.role == 'CONSUMER':
        from .models import ConsumerTier
        basic_tier = ConsumerTier.objects.get(name='BASIC')
        
        ConsumerProfile.objects.create(
            user=instance,
            tier=basic_tier,
            subscription_active=True  # Tier básico es gratis
        )