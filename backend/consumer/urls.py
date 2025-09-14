from django.urls import path, include
from .views import (
    QRVerificationView,
    PublicAnimalHistoryView,
    GenerateQRView,
    AnimalSearchView,
    CertificationVerificationView,
    BlockchainProofView,
    PublicAPIDocsView
)

urlpatterns = [
    # -------------------------------------------------------------------------
    # VERIFICACIÓN Y QR
    # -------------------------------------------------------------------------
    path(
        'verify/', 
        QRVerificationView.as_view(), 
        name='verify-qr',
        kwargs={'description': 'Verificar animal mediante QR code o token ID'}
    ),
    
    # -------------------------------------------------------------------------
    # INFORMACIÓN PÚBLICA DE ANIMALES
    # -------------------------------------------------------------------------
    path(
        'animal/<int:animal_id>/history/', 
        PublicAnimalHistoryView.as_view(), 
        name='public-animal-history',
        kwargs={'description': 'Obtener historial público completo de un animal'}
    ),
    path(
        'animal/<int:animal_id>/qr/', 
        GenerateQRView.as_view(), 
        name='generate-qr',
        kwargs={'description': 'Generar código QR para un animal'}
    ),
    path(
        'animal/<int:animal_id>/proof/', 
        BlockchainProofView.as_view(), 
        name='blockchain-proof',
        kwargs={'description': 'Obtener cadena de proof blockchain de un animal'}
    ),
    
    # -------------------------------------------------------------------------
    # BÚSQUEDA Y CONSULTA
    # -------------------------------------------------------------------------
    path(
        'search/', 
        AnimalSearchView.as_view(), 
        name='animal-search',
        kwargs={'description': 'Buscar animales públicos en el sistema'}
    ),
    
    # -------------------------------------------------------------------------
    # VERIFICACIÓN DE CERTIFICACIONES
    # -------------------------------------------------------------------------
    path(
        'certification/<int:certification_id>/verify/', 
        CertificationVerificationView.as_view(), 
        name='certification-verify',
        kwargs={'description': 'Verificar una certificación específica'}
    ),
    
    # -------------------------------------------------------------------------
    # DOCUMENTACIÓN Y METADATOS
    # -------------------------------------------------------------------------
    path(
        'docs/', 
        PublicAPIDocsView.as_view(), 
        name='public-api-docs',
        kwargs={'description': 'Documentación de la API pública para consumidores'}
    ),
]

# Para incluir en el urls.py principal
app_name = 'consumer'

# Documentación de parámetros de query disponibles
CONSUMER_QUERY_PARAMS = {
    'verify': {
        'qr': 'Datos del código QR',
        'token_id': 'ID del token NFT del animal'
    },
    'search': {
        'q': 'Término de búsqueda (ear_tag, breed, token_id)',
        'breed': 'Filtrar por raza',
        'health_status': 'Filtrar por estado de salud'
    }
}

# Ejemplos de uso para documentación
CONSUMER_API_EXAMPLES = {
    'verification': {
        'qr_code': '/api/consumer/verify/?qr=GANADOCHAIN_ANIMAL_123',
        'token_id': '/api/consumer/verify/?token_id=456'
    },
    'animal_info': {
        'history': '/api/consumer/animal/123/history/',
        'qr_code': '/api/consumer/animal/123/qr/',
        'blockchain_proof': '/api/consumer/animal/123/proof/'
    },
    'search': {
        'general': '/api/consumer/search/?q=Angus',
        'filtered': '/api/consumer/search/?breed=Hereford&health_status=HEALTHY'
    },
    'certification': {
        'verify': '/api/consumer/certification/789/verify/'
    },
    'docs': {
        'api_docs': '/api/consumer/docs/'
    }
}

# Versión con router para posibles expansiones futuras
consumer_urlpatterns = urlpatterns

# Si en el futuro necesitas versionado de API
versioned_patterns = [
    path('v1/', include((consumer_urlpatterns, 'consumer-v1'))),
]

# Para incluir en el urls.py principal de Django:
# path('api/consumer/', include('consumer.urls')),