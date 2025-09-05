from rest_framework import permissions

class IsDeviceOwner(permissions.BasePermission):
    """
    Permiso personalizado para verificar que el usuario es dueño del dispositivo
    o de objetos relacionados con el dispositivo.
    """
    
    def has_object_permission(self, request, view, obj):
        # Para IoTDevice
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        # Para DeviceConfiguration (accede a través del dispositivo)
        if hasattr(obj, 'device') and hasattr(obj.device, 'owner'):
            return obj.device.owner == request.user
        
        # Para datos GPS y Health (accede a través del animal → owner)
        if hasattr(obj, 'animal') and hasattr(obj.animal, 'owner'):
            return obj.animal.owner == request.user
        
        # Para eventos de dispositivo
        if hasattr(obj, 'device') and hasattr(obj.device, 'owner'):
            return obj.device.owner == request.user
        
        return False

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsIoTDevice(permissions.BasePermission):
    """
    Permiso para dispositivos IoT (autenticación por API key o token especial)
    """
    def has_permission(self, request, view):
        # Implementar lógica de autenticación para dispositivos IoT
        # Por ejemplo, verificar API key en headers
        device_token = request.headers.get('X-Device-Token')
        device_id = request.headers.get('X-Device-ID')
        
        if device_token and device_id:
            try:
                from .models import IoTDevice
                device = IoTDevice.objects.get(
                    device_id=device_id,
                    auth_token=device_token,  # Necesitarías añadir este campo al modelo
                    is_active=True
                )
                request.device = device  # Almacenar dispositivo en la request
                return True
            except IoTDevice.DoesNotExist:
                return False
        
        return False