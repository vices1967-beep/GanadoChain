from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'iot'

router = DefaultRouter()
router.register(r'devices', views.IoTDeviceViewSet, basename='iotdevice')
router.register(r'gps-data', views.GPSDataViewSet, basename='gpsdata')
router.register(r'health-data', views.HealthSensorDataViewSet, basename='healthsensordata')
router.register(r'device-events', views.DeviceEventViewSet, basename='deviceevent')
router.register(r'device-configs', views.DeviceConfigurationViewSet, basename='deviceconfiguration')
router.register(r'device-analytics', views.DeviceAnalyticsViewSet, basename='deviceanalytics')

urlpatterns = [
    # Ingesta de datos (para dispositivos)
    path('ingest/', views.IoTDataIngestView.as_view(), name='data-ingest'),
    path('ingest/bulk/', views.BulkDataIngestView.as_view(), name='bulk-data-ingest'),
    path('register/', views.DeviceRegistrationView.as_view(), name='device-register'),
    
    # Estadísticas
    path('stats/', views.IoTStatsView.as_view(), name='iot-stats'),
    
    # Alertas y configuración
    path('devices/<str:device_id>/alerts/', views.AlertThresholdView.as_view(), name='device-alerts'),
    
    # Rutas específicas
    path('gps/animal/<int:animal_id>/track/', views.GPSDataViewSet.as_view({'get': 'animal_track'}), name='animal-gps-track'),
    path('health/animal/<int:animal_id>/', views.HealthSensorDataViewSet.as_view({'get': 'animal_health'}), name='animal-health-history'),
    path('health/alerts/', views.HealthSensorDataViewSet.as_view({'get': 'health_alerts'}), name='health-alerts'),
    path('events/unresolved/', views.DeviceEventViewSet.as_view({'get': 'unresolved'}), name='unresolved-events'),
    
    # Incluir rutas del router
    path('', include(router.urls)),
]