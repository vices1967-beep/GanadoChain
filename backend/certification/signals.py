# backend/certification/signals.py
from django.db.models.signals import post_save, pre_save, m2m_changed
from django.dispatch import receiver
from django.utils import timezone
from .models import Certification, CertificationStandard, GlobalCertificationBody
from users.models import User
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=GlobalCertificationBody)
def setup_certification_body(sender, instance, created, **kwargs):
    """Configurar automáticamente un nuevo organismo de certificación"""
    if created:
        try:
            # Habilitar multichain para el usuario administrador
            if instance.admin_user and not instance.admin_user.multichain_enabled:
                instance.admin_user.enable_multichain()
                
            # Configurar redes preferidas si no están configuradas
            if not instance.preferred_networks.exists() and instance.blockchain_enabled:
                from core.multichain.models import BlockchainNetwork
                default_networks = BlockchainNetwork.objects.filter(
                    is_active=True, supports_smart_contracts=True
                ).order_by('priority')[:2]
                instance.preferred_networks.set(default_networks)
                
            logger.info(f"Certification body {instance.name} setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up certification body: {str(e)}")

@receiver(pre_save, sender=Certification)
def validate_certification_changes(sender, instance, **kwargs):
    """Validar cambios en certificaciones"""
    if instance.pk:
        try:
            original = Certification.objects.get(pk=instance.pk)
            
            # Validar transiciones de estado
            if (original.status == 'APPROVED' and 
                instance.status in ['SUSPENDED', 'REVOKED'] and 
                not instance.suspension_reason and not instance.revocation_cause):
                
                from django.core.exceptions import ValidationError
                raise ValidationError(
                    "Se requiere una razón para suspender o revocar una certificación aprobada."
                )
                
        except Certification.DoesNotExist:
            pass

@receiver(post_save, sender=Certification)
def handle_certification_approval(sender, instance, created, **kwargs):
    """Manejar aprobación de certificaciones"""
    if not created and instance.status == 'APPROVED':
        from .tasks import (
            issue_blockchain_certificate, 
            send_certification_approval_notification,
            update_entity_reputation
        )
        
        # Emitir certificado en blockchain si está habilitado
        if instance.blockchain_certificate:
            issue_blockchain_certificate.delay(instance.id)
        
        # Enviar notificaciones
        send_certification_approval_notification.delay(instance.id)
        
        # Actualizar reputación de la entidad certificada
        update_entity_reputation.delay(instance.certified_entity.id, 'CERTIFICATION_APPROVED')

@receiver(m2m_changed, sender=Certification.animals.through)
def update_animal_certification_status(sender, instance, action, **kwargs):
    """Actualizar estado de certificación de animales cuando se modifican relaciones"""
    if action in ['post_add', 'post_remove', 'post_clear']:
        if instance.scope_type == 'ANIMAL':
            # Actualizar metadatos de certificación para animales
            instance.update_animal_certification_metadata()

@receiver(m2m_changed, sender=Certification.batches.through)
def update_batch_certification_status(sender, instance, action, **kwargs):
    """Actualizar estado de certificación de lotes cuando se modifican relaciones"""
    if action in ['post_add', 'post_remove', 'post_clear']:
        if instance.scope_type == 'BATCH':
            # Actualizar metadatos de certificación para lotes
            instance.update_batch_certification_metadata()