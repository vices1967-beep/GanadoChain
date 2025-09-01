from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'cattle'

# Router para ViewSets
router = DefaultRouter()
router.register(r'animals', views.AnimalViewSet, basename='animal')
router.register(r'health-records', views.AnimalHealthRecordViewSet, basename='animalhealthrecord')
router.register(r'batches', views.BatchViewSet, basename='batch')
router.register(r'iot-devices', views.IoTDeviceViewSet, basename='iotdevice')

urlpatterns = [
    # URLs de ViewSets
    path('', include(router.urls)),
    
    # URLs específicas para acciones de animales
    path('animals/<int:pk>/mint-nft/', views.AnimalViewSet.as_view({'post': 'mint_nft'}), name='animal-mint-nft'),
    path('animals/<int:pk>/verify-nft/', views.AnimalViewSet.as_view({'get': 'verify_nft'}), name='animal-verify-nft'),
    path('animals/<int:pk>/nft-info/', views.AnimalViewSet.as_view({'get': 'nft_info'}), name='animal-nft-info'),
    path('animals/<int:pk>/health-records/', views.AnimalViewSet.as_view({'get': 'health_records'}), name='animal-health-records'),
    
    # URLs específicas para acciones de lotes
    path('batches/<int:pk>/add-animals/', views.BatchViewSet.as_view({'post': 'add_animals'}), name='batch-add-animals'),
    path('batches/<int:pk>/remove-animals/', views.BatchViewSet.as_view({'post': 'remove_animals'}), name='batch-remove-animals'),
    
    # URLs específicas para dispositivos IoT
    path('iot-devices/health-data/', views.IoTDeviceViewSet.as_view({'post': 'health_data'}), name='iot-device-health-data'),
    
    # URLs de estadísticas
    path('stats/', views.cattle_stats, name='cattle-stats'),
    
    # URLs de operaciones adicionales (mantenidas por compatibilidad)
    #path('animals-list/', views.AnimalListCreateView.as_view(), name='animal_list_create'),
    #path('animals-detail/<int:pk>/', views.AnimalDetailView.as_view(), name='animal_detail'),
    #path('batches-list/', views.BatchListCreateView.as_view(), name='batch_list_create'),
    #path('batches-detail/<int:pk>/', views.BatchDetailView.as_view(), name='batch_detail'),
]

# URLs para API docs y exploración
urlpatterns += [
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]