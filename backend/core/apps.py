# backend/core/apps.py
from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Núcleo Multichain'
    
    # def ready(self):
    #     # Importar señales y configuraciones
    #     # import core.signals
    #     # # Cargar redes por defecto
    #     # from core.utils import load_default_networks
    #     # load_default_networks()