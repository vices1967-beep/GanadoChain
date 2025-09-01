from rest_framework import permissions
from .models import IoTDevice

class IsDeviceOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class IsIoTDevice(permissions.BasePermission):
    def has_permission(self, request, view):
        # Autenticación por API Key para dispositivos IoT
        api_key = request.headers.get('X-IoT-API-Key')
        if not api_key:
            return False
        
        try:
            device = IoTDevice.objects.get(device_id=api_key, is_active=True)
            request.device = device  # Attach device to request
            return True
        except IoTDevice.DoesNotExist:
            return False