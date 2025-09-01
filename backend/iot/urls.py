from django.urls import path
from . import views

app_name = 'iot'

urlpatterns = [
    path('devices/', views.IoTDeviceListCreateView.as_view(), name='device-list'),
    path('devices/<int:pk>/', views.IoTDeviceDetailView.as_view(), name='device-detail'),
    path('gps-data/', views.GPSDataListView.as_view(), name='gps-data'),
    path('health-data/', views.HealthDataListView.as_view(), name='health-data'),
    path('ingest/', views.IoTDataIngestView.as_view(), name='data-ingest'),
]