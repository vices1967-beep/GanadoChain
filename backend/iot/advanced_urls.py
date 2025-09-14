from django.urls import path
from .advanced_views import DeviceFirmwareUpdateView, BulkDeviceManagementView, IoTNetworkHealthView, PredictiveMaintenanceView

urlpatterns = [
    path('firmware/<str:device_id>/', DeviceFirmwareUpdateView.as_view(), name='firmware-update'),
    path('bulk-management/', BulkDeviceManagementView.as_view(), name='bulk-device-management'),
    path('network-health/', IoTNetworkHealthView.as_view(), name='network-health'),
    path('predictive-maintenance/', PredictiveMaintenanceView.as_view(), name='predictive-maintenance'),
]
