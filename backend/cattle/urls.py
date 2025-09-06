from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'cattle'

router = DefaultRouter()
router.register(r'animals', views.AnimalViewSet, basename='animal')
router.register(r'health-records', views.AnimalHealthRecordViewSet, basename='animalhealthrecord')
router.register(r'batches', views.BatchViewSet, basename='batch')
router.register(r'blockchain-events', views.BlockchainEventStateViewSet, basename='blockchaineventstate')
router.register(r'audit-trail', views.CattleAuditTrailViewSet, basename='cattleaudittrail')

urlpatterns = [
    # Operaciones específicas
    path('animals/search/', views.search_animals, name='animal-search'),
    path('batches/search/', views.search_batches, name='batch-search'),
    path('stats/', views.cattle_stats, name='cattle-stats'),
    
    # NFT y blockchain - ANIMAL
    path('animals/<int:pk>/mint-nft/', views.AnimalViewSet.as_view({'post': 'mint_nft'}), name='animal-mint-nft'),
    path('animals/<int:pk>/transfer/', views.AnimalViewSet.as_view({'post': 'transfer'}), name='animal-transfer'),
    path('animals/<int:pk>/update-health/', views.AnimalViewSet.as_view({'post': 'update_health'}), name='animal-update-health'),
    path('animals/<int:pk>/verify-nft/', views.AnimalViewSet.as_view({'get': 'verify_nft'}), name='animal-verify-nft'),
    path('animals/<int:pk>/nft-info/', views.AnimalViewSet.as_view({'get': 'nft_info'}), name='animal-nft-info'),
    path('animals/<int:pk>/health-records/', views.AnimalViewSet.as_view({'get': 'health_records'}), name='animal-health-records'),
    path('animals/<int:pk>/blockchain-events/', views.AnimalViewSet.as_view({'get': 'blockchain_events'}), name='animal-blockchain-events'),
    path('animals/<int:pk>/audit-trail/', views.AnimalViewSet.as_view({'get': 'audit_trail'}), name='animal-audit-trail'),
    
    # Operaciones de BATCH
    path('batches/<int:pk>/update-status/', views.BatchViewSet.as_view({'post': 'update_status'}), name='batch-update-status'),
    path('batches/<int:pk>/add-animals/', views.BatchViewSet.as_view({'post': 'add_animals'}), name='batch-add-animals'),
    path('batches/<int:pk>/remove-animals/', views.BatchViewSet.as_view({'post': 'remove_animals'}), name='batch-remove-animals'),
    path('batches/<int:pk>/blockchain-events/', views.BatchViewSet.as_view({'get': 'blockchain_events'}), name='batch-blockchain-events'),
    path('batches/<int:pk>/audit-trail/', views.BatchViewSet.as_view({'get': 'audit_trail'}), name='batch-audit-trail'),
    
    # Incluir rutas del router
    path('', include(router.urls)),
]