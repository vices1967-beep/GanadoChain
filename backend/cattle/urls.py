from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'cattle'

router = DefaultRouter()
router.register(r'animals', views.AnimalViewSet, basename='animal')
router.register(r'health-records', views.AnimalHealthRecordViewSet, basename='animalhealthrecord')
router.register(r'batches', views.BatchViewSet, basename='batch')

urlpatterns = [
    path('', include(router.urls)),
    path('animals/<int:pk>/mint-nft/', views.AnimalViewSet.as_view({'post': 'mint_nft'}), name='animal-mint-nft'),
    path('animals/<int:pk>/verify-nft/', views.AnimalViewSet.as_view({'get': 'verify_nft'}), name='animal-verify-nft'),
    path('animals/<int:pk>/nft-info/', views.AnimalViewSet.as_view({'get': 'nft_info'}), name='animal-nft-info'),
    path('animals/<int:pk>/health-records/', views.AnimalViewSet.as_view({'get': 'health_records'}), name='animal-health-records'),
    path('batches/<int:pk>/add-animals/', views.BatchViewSet.as_view({'post': 'add_animals'}), name='batch-add-animals'),
    path('batches/<int:pk>/remove-animals/', views.BatchViewSet.as_view({'post': 'remove_animals'}), name='batch-remove-animals'),
    path('stats/', views.cattle_stats, name='cattle-stats'),
]