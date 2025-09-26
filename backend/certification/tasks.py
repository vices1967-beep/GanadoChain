# backend/certification/tasks.py
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import logging
from .models import Certification, GlobalCertificationBody

logger = logging.getLogger(__name__)

@shared_task
def issue_blockchain_certificate(certification_id):
    """Emitir certificado en blockchain"""
    try:
        certification = Certification.objects.get(id=certification_id)
        
        if not certification.blockchain_certificate:
            # Lógica para emitir en blockchain
            from core.multichain.manager import multichain_manager
            
            # Preparar datos del certificado
            certificate_data = {
                'certificate_number': certification.certificate_number,
                'entity_id': certification.certified_entity.id,
                'standard_code': certification.standard.full_code,
                'issue_date': certification.issue_date.isoformat(),
                'expiry_date': certification.expiry_date.isoformat(),
                'grade': certification.final_grade,
                'score': str(certification.audit_score),
                'auditor_id': certification.auditor.id if certification.auditor else None,
            }
            
            # Emitir en la red preferida del organismo
            certification_body = certification.standard.certification_body
            preferred_network = certification_body.preferred_networks.first()
            
            if preferred_network:
                result = multichain_manager.issue_certificate(
                    network_id=preferred_network.network_id,
                    certificate_data=certificate_data,
                    issuer_address=certification_body.admin_user.wallet_address
                )
                
                if result['success']:
                    certification.blockchain_certificate = True
                    certification.save()
                    logger.info(f"Blockchain certificate issued for {certification.certificate_number}")
                else:
                    logger.error(f"Failed to issue blockchain certificate: {result['error']}")
        
    except Exception as e:
        logger.error(f"Error issuing blockchain certificate: {str(e)}")

@shared_task
def send_certification_approval_notification(certification_id):
    """Enviar notificación de aprobación de certificación"""
    try:
        certification = Certification.objects.get(id=certification_id)
        
        subject = f"Certificación Aprobada - {certification.certificate_number}"
        message = f"""
        Su certificación ha sido aprobada exitosamente.
        
        Detalles:
        - Certificado: {certification.certificate_number}
        - Estándar: {certification.standard.name}
        - Grado: {certification.final_grade}
        - Válido hasta: {certification.expiry_date}
        
        Felicitaciones por este logro.
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [certification.certified_entity.email],
            fail_silently=False,
        )
        
    except Exception as e:
        logger.error(f"Error sending certification approval notification: {str(e)}")

@shared_task
def check_expiring_certifications():
    """Verificar certificaciones próximas a expirar"""
    try:
        warning_date = timezone.now().date() + timezone.timedelta(days=30)
        expiring_certifications = Certification.objects.filter(
            expiry_date__lte=warning_date,
            status='APPROVED'
        )
        
        for certification in expiring_certifications:
            send_certification_expiry_warning.delay(certification.id)
            
    except Exception as e:
        logger.error(f"Error checking expiring certifications: {str(e)}")

@shared_task
def send_certification_expiry_warning(certification_id):
    """Enviar advertencia de expiración de certificación"""
    try:
        certification = Certification.objects.get(id=certification_id)
        days_until_expiry = certification.days_until_expiry
        
        subject = f"Certificación Próxima a Expirar - {certification.certificate_number}"
        message = f"""
        Su certificación expirará en {days_until_expiry} días.
        
        Detalles:
        - Certificado: {certification.certificate_number}
        - Estándar: {certification.standard.name}
        - Fecha de expiración: {certification.expiry_date}
        
        Por favor, inicie el proceso de renovación.
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [certification.certified_entity.email],
            fail_silently=False,
        )
        
    except Exception as e:
        logger.error(f"Error sending certification expiry warning: {str(e)}")