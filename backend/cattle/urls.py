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
    
    # NFT y blockchain
    path('animals/<int:pk>/mint-nft/', views.AnimalViewSet.as_view({'post': 'mint_nft'}), name='animal-mint-nft'),
    path('animals/<int:pk>/transfer/', views.AnimalViewSet.as_view({'post': 'transfer'}), name='animal-transfer'),
    path('animals/<int:pk>/update-health/', views.AnimalViewSet.as_view({'post': 'update_health'}), name='animal-update-health'),
    
    # Incluir rutas del router
    path('', include(router.urls)),
]