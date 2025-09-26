from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'cattle'

router = DefaultRouter()
# -------------------------------------------------------------------------
# RUTAS PRINCIPALES (CRUD BÁSICO)
# -------------------------------------------------------------------------
router.register(r'animals', views.AnimalViewSet, basename='animal')
router.register(r'health-records', views.AnimalHealthRecordViewSet, basename='animalhealthrecord')
router.register(r'batches', views.BatchViewSet, basename='batch')
router.register(r'blockchain-events', views.BlockchainEventStateViewSet, basename='blockchaineventstate')
router.register(r'audit-trail', views.CattleAuditTrailViewSet, basename='cattleaudittrail')

# -------------------------------------------------------------------------
# RUTAS MULTICHAIN (NUEVAS)
# -------------------------------------------------------------------------
router.register(r'animals-multichain', views.AnimalMultichainViewSet, basename='animalmultichain')
router.register(r'nft-mirrors', views.AnimalNFTMirrorViewSet, basename='animalnftmirror')

urlpatterns = [
    # -------------------------------------------------------------------------
    # OPERACIONES ESPECÍFICAS - BÚSQUEDA Y ESTADÍSTICAS
    # -------------------------------------------------------------------------
    path(
        'animals/search/', 
        views.search_animals, 
        name='animal-search',
        kwargs={'description': 'Búsqueda avanzada de animales con múltiples filtros'}
    ),
    path(
        'batches/search/', 
        views.search_batches, 
        name='batch-search',
        kwargs={'description': 'Búsqueda avanzada de lotes con múltiples filtros'}
    ),
    path(
        'stats/', 
        views.cattle_stats, 
        name='cattle-stats',
        kwargs={'description': 'Estadísticas generales del ganado y lotes'}
    ),
    
    # -------------------------------------------------------------------------
    # OPERACIONES NFT Y BLOCKCHAIN - ANIMAL
    # -------------------------------------------------------------------------
    path(
        'animals/<int:pk>/mint-nft/', 
        views.AnimalViewSet.as_view({'post': 'mint_nft'}), 
        name='animal-mint-nft',
        kwargs={'description': 'Mintear NFT del animal en blockchain primaria'}
    ),
    path(
        'animals/<int:pk>/transfer/', 
        views.AnimalViewSet.as_view({'post': 'transfer'}), 
        name='animal-transfer',
        kwargs={'description': 'Transferir NFT del animal a nueva dirección'}
    ),
    path(
        'animals/<int:pk>/update-health/', 
        views.AnimalViewSet.as_view({'post': 'update_health'}), 
        name='animal-update-health',
        kwargs={'description': 'Actualizar registro de salud del animal'}
    ),
    path(
        'animals/<int:pk>/verify-nft/', 
        views.AnimalViewSet.as_view({'get': 'verify_nft'}), 
        name='animal-verify-nft',
        kwargs={'description': 'Verificar autenticidad del NFT en blockchain'}
    ),
    path(
        'animals/<int:pk>/nft-info/', 
        views.AnimalViewSet.as_view({'get': 'nft_info'}), 
        name='animal-nft-info',
        kwargs={'description': 'Obtener información completa del NFT'}
    ),
    path(
        'animals/<int:pk>/health-records/', 
        views.AnimalViewSet.as_view({'get': 'health_records'}), 
        name='animal-health-records',
        kwargs={'description': 'Obtener historial completo de salud del animal'}
    ),
    path(
        'animals/<int:pk>/blockchain-events/', 
        views.AnimalViewSet.as_view({'get': 'blockchain_events'}), 
        name='animal-blockchain-events',
        kwargs={'description': 'Obtener eventos blockchain del animal'}
    ),
    path(
        'animals/<int:pk>/audit-trail/', 
        views.AnimalViewSet.as_view({'get': 'audit_trail'}), 
        name='animal-audit-trail',
        kwargs={'description': 'Obtener trail de auditoría del animal'}
    ),
    
    # -------------------------------------------------------------------------
    # OPERACIONES DE BATCH (LOTES)
    # -------------------------------------------------------------------------
    path(
        'batches/<int:pk>/update-status/', 
        views.BatchViewSet.as_view({'post': 'update_status'}), 
        name='batch-update-status',
        kwargs={'description': 'Actualizar estado del lote'}
    ),
    path(
        'batches/<int:pk>/add-animals/', 
        views.BatchViewSet.as_view({'post': 'add_animals'}), 
        name='batch-add-animals',
        kwargs={'description': 'Añadir animales al lote'}
    ),
    path(
        'batches/<int:pk>/remove-animals/', 
        views.BatchViewSet.as_view({'post': 'remove_animals'}), 
        name='batch-remove-animals',
        kwargs={'description': 'Remover animales del lote'}
    ),
    path(
        'batches/<int:pk>/blockchain-events/', 
        views.BatchViewSet.as_view({'get': 'blockchain_events'}), 
        name='batch-blockchain-events',
        kwargs={'description': 'Obtener eventos blockchain del lote'}
    ),
    path(
        'batches/<int:pk>/audit-trail/', 
        views.BatchViewSet.as_view({'get': 'audit_trail'}), 
        name='batch-audit-trail',
        kwargs={'description': 'Obtener trail de auditoría del lote'}
    ),
    
    # -------------------------------------------------------------------------
    # OPERACIONES MULTICHAIN ESPECÍFICAS (NUEVAS)
    # -------------------------------------------------------------------------
    path(
        'animals/<int:pk>/create-multichain-profile/', 
        views.AnimalMultichainViewSet.as_view({'post': 'create'}), 
        name='animal-create-multichain',
        kwargs={'description': 'Crear perfil multichain para el animal'}
    ),
    path(
        'animals-multichain/<int:pk>/register-blockchain/', 
        views.AnimalMultichainViewSet.as_view({'post': 'register_on_blockchain'}), 
        name='animal-register-blockchain',
        kwargs={'description': 'Registrar animal multichain en blockchain primaria'}
    ),
    path(
        'animals-multichain/<int:pk>/create-mirror/', 
        views.AnimalMultichainViewSet.as_view({'post': 'create_mirror'}), 
        name='animal-create-mirror',
        kwargs={'description': 'Crear espejo del NFT en otra blockchain'}
    ),
    path(
        'animals-multichain/<int:pk>/mirrors/', 
        views.AnimalMultichainViewSet.as_view({'get': 'mirrors'}), 
        name='animal-mirrors-list',
        kwargs={'description': 'Listar todos los espejos del animal multichain'}
    ),
    path(
        'animals-multichain/<int:pk>/blockchain-status/', 
        views.AnimalMultichainViewSet.as_view({'get': 'blockchain_status'}), 
        name='animal-blockchain-status',
        kwargs={'description': 'Obtener estado blockchain completo del animal'}
    ),
    
    # -------------------------------------------------------------------------
    # INCLUIR RUTAS DEL ROUTER (CRUD AUTOMÁTICO)
    # -------------------------------------------------------------------------
    path('', include(router.urls)),
]

# Documentación de parámetros de query disponibles
CATTLE_QUERY_PARAMS = {
    'animal-search': {
        'q': 'Término de búsqueda general',
        'breed': 'Filtrar por raza',
        'health_status': 'Filtrar por estado de salud',
        'owner_id': 'Filtrar por propietario',
        'batch_id': 'Filtrar por lote'
    },
    'batch-search': {
        'q': 'Término de búsqueda general',
        'status': 'Filtrar por estado del lote',
        'owner_id': 'Filtrar por propietario',
        'min_animals': 'Mínimo número de animales',
        'max_animals': 'Máximo número de animales'
    },
    'animals-multichain': {
        'network': 'Filtrar por red blockchain',
        'is_cross_chain': 'Filtrar por estado cross-chain (true/false)',
        'has_primary_nft': 'Filtrar por animales con NFT primario'
    },
    'nft-mirrors': {
        'network': 'Filtrar por red blockchain específica',
        'is_active': 'Filtrar por espejos activos (true/false)',
        'animal_id': 'Filtrar por animal específico'
    }
}

# Ejemplos de uso para documentación
CATTLE_API_EXAMPLES = {
    'animals': {
        'list': '/api/cattle/animals/',
        'search': '/api/cattle/animals/search/?q=Angus&health_status=HEALTHY',
        'detail': '/api/cattle/animals/123/',
        'nft_operations': {
            'mint': '/api/cattle/animals/123/mint-nft/',
            'verify': '/api/cattle/animals/123/verify-nft/',
            'info': '/api/cattle/animals/123/nft-info/'
        }
    },
    'batches': {
        'list': '/api/cattle/batches/',
        'search': '/api/cattle/batches/search/?status=ACTIVE&min_animals=10',
        'detail': '/api/cattle/batches/456/',
        'operations': {
            'add_animals': '/api/cattle/batches/456/add-animals/',
            'update_status': '/api/cattle/batches/456/update-status/'
        }
    },
    'multichain': {
        'profiles': '/api/cattle/animals-multichain/',
        'create_profile': '/api/cattle/animals/123/create-multichain-profile/',
        'register': '/api/cattle/animals-multichain/789/register-blockchain/',
        'create_mirror': '/api/cattle/animals-multichain/789/create-mirror/',
        'mirrors': '/api/cattle/animals-multichain/789/mirrors/',
        'status': '/api/cattle/animals-multichain/789/blockchain-status/'
    },
    'health': {
        'records': '/api/cattle/health-records/',
        'animal_health': '/api/cattle/animals/123/health-records/'
    },
    'blockchain': {
        'events': '/api/cattle/blockchain-events/',
        'animal_events': '/api/cattle/animals/123/blockchain-events/',
        'batch_events': '/api/cattle/batches/456/blockchain-events/'
    },
    'audit': {
        'trail': '/api/cattle/audit-trail/',
        'animal_audit': '/api/cattle/animals/123/audit-trail/',
        'batch_audit': '/api/cattle/batches/456/audit-trail/'
    }
}

# Mapa completo de endpoints para documentación
CATTLE_ENDPOINTS_MAP = {
    'animals_crud': {
        'path': '/api/cattle/animals/',
        'method': 'GET, POST, PUT, DELETE',
        'description': 'CRUD completo para animales',
        'parameters': {
            'breed': 'str (opcional)',
            'health_status': 'str (opcional)'
        }
    },
    'animals_search': {
        'path': '/api/cattle/animals/search/',
        'method': 'GET',
        'description': 'Búsqueda avanzada de animales',
        'parameters': CATTLE_QUERY_PARAMS['animal-search']
    },
    'animal_nft_mint': {
        'path': '/api/cattle/animals/{id}/mint-nft/',
        'method': 'POST',
        'description': 'Mintear NFT del animal en blockchain',
        'parameters': {
            'network_id': 'int (opcional)'
        }
    },
    'batches_crud': {
        'path': '/api/cattle/batches/',
        'method': 'GET, POST, PUT, DELETE',
        'description': 'CRUD completo para lotes',
        'parameters': {}
    },
    'animals_multichain_crud': {
        'path': '/api/cattle/animals-multichain/',
        'method': 'GET, POST, PUT, DELETE',
        'description': 'CRUD completo para perfiles multichain de animales',
        'parameters': CATTLE_QUERY_PARAMS['animals-multichain']
    },
    'animal_register_blockchain': {
        'path': '/api/cattle/animals-multichain/{id}/register-blockchain/',
        'method': 'POST',
        'description': 'Registrar animal multichain en blockchain primaria',
        'parameters': {
            'network_id': 'int (opcional)'
        }
    },
    'animal_create_mirror': {
        'path': '/api/cattle/animals-multichain/{id}/create-mirror/',
        'method': 'POST',
        'description': 'Crear espejo del NFT en otra blockchain',
        'parameters': {
            'network_id': 'int (requerido)'
        }
    },
    'animal_mirrors_list': {
        'path': '/api/cattle/animals-multichain/{id}/mirrors/',
        'method': 'GET',
        'description': 'Listar espejos del animal multichain',
        'parameters': {}
    },
    'animal_blockchain_status': {
        'path': '/api/cattle/animals-multichain/{id}/blockchain-status/',
        'method': 'GET',
        'description': 'Obtener estado blockchain completo del animal',
        'parameters': {}
    }
}

# Versión con router para posibles expansiones futuras
cattle_urlpatterns = urlpatterns

# Si en el futuro necesitas versionado de API
versioned_patterns = [
    path('v1/', include((cattle_urlpatterns, 'cattle-v1'))),
]

# Para incluir en el urls.py principal de Django:
# path('api/cattle/', include('cattle.urls')),