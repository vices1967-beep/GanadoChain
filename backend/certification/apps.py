# backend/certification/apps.py
from django.apps import AppConfig

class CertificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'certification'
    verbose_name = 'Sistema de Certificación'

    def ready(self):
        # Importar señales
        import certification.signals
        
        # Configurar tareas periódicas
        from .tasks import check_expiring_certifications
        from celery.schedules import crontab
        
        # Esto se configurará en settings.py de Celery