from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'iot'

# Router para ViewSets
router = DefaultRouter()
router.register(r'devices', views.IoTDeviceViewSet, basename='iotdevice')
router.register(r'gps-data', views.GPSDataViewSet, basename='gpsdata')
router.register(r'health-data', views.HealthSensorDataViewSet, basename='healthsensordata')
router.register(r'events', views.DeviceEventViewSet, basename='deviceevent')

urlpatterns = [
    # URLs de ViewSets
    path('', include(router.urls)),
    
    # URLs de ingesta de datos
    path('ingest/', views.IoTDataIngestView.as_view(), name='data-ingest'),
    path('ingest/bulk/', views.BulkDataIngestView.as_view(), name='bulk-data-ingest'),
    
    # URLs de gestión de dispositivos
    path('register/', views.DeviceRegistrationView.as_view(), name='device-registration'),
    
    # URLs de estadísticas y monitoreo
    path('stats/', views.IoTStatsView.as_view(), name='iot-stats'),
    
    # URLs específicas para acciones personalizadas
    path('devices/<int:pk>/update-status/', views.IoTDeviceViewSet.as_view({'post': 'update_status'}), name='device-update-status'),
    path('devices/<int:pk>/events/', views.IoTDeviceViewSet.as_view({'get': 'events'}), name='device-events'),
    path('devices/<int:pk>/stats/', views.IoTDeviceViewSet.as_view({'get': 'stats'}), name='device-stats'),
    
    path('gps-data/latest/', views.GPSDataViewSet.as_view({'get': 'latest'}), name='gps-data-latest'),
    path('gps-data/animal/<int:animal_id>/track/', views.GPSDataViewSet.as_view({'get': 'animal_track'}), name='gps-animal-track'),
    
    path('health-data/latest/', views.HealthSensorDataViewSet.as_view({'get': 'latest'}), name='health-data-latest'),
    path('health-data/animal/<int:animal_id>/health/', views.HealthSensorDataViewSet.as_view({'get': 'animal_health'}), name='health-animal-history'),
    
    # URLs de compatibilidad (mantenidas para versiones anteriores)
    #path('devices-list/', views.IoTDeviceListCreateView.as_view(), name='device-list-legacy'),
    #path('devices-detail/<int:pk>/', views.IoTDeviceDetailView.as_view(), name='device-detail-legacy'),
    #path('gps-data-list/', views.GPSDataListView.as_view(), name='gps-data-legacy'),
    #path('health-data-list/', views.HealthDataListView.as_view(), name='health-data-legacy'),
]

# URLs para API docs y exploración
urlpatterns += [
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]