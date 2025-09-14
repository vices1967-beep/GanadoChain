from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import IoTDevice, DeviceEvent
from .serializers import IoTDeviceSerializer
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

class DeviceFirmwareUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, device_id):
        device = get_object_or_404(IoTDevice, device_id=device_id, owner=request.user)
        firmware_version = request.data.get('firmware_version')
        
        if not firmware_version:
            return Response({'error': 'firmware_version requerido'}, status=400)
        
        # Simular actualización de firmware
        device.firmware_version = firmware_version
        device.save()
        
        # Registrar evento
        DeviceEvent.objects.create(
            device=device,
            event_type='FIRMWARE_UPDATE',
            severity='MEDIUM',
            message=f'Firmware actualizado a versión {firmware_version}',
            data={'old_version': device.firmware_version, 'new_version': firmware_version}
        )
        
        return Response({
            'success': True,
            'message': 'Firmware actualizado',
            'device_id': device.device_id,
            'new_version': firmware_version
        })

class BulkDeviceManagementView(APIView):
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        action_type = request.data.get('action')
        device_ids = request.data.get('device_ids', [])
        
        if not action_type or not device_ids:
            return Response({
                'error': 'action y device_ids requeridos'
            }, status=400)
        
        devices = IoTDevice.objects.filter(device_id__in=device_ids)
        
        if action_type == 'update_firmware':
            firmware_version = request.data.get('firmware_version')
            if not firmware_version:
                return Response({'error': 'firmware_version requerido'}, status=400)
            
            updated_count = devices.update(firmware_version=firmware_version)
            
            return Response({
                'success': True,
                'message': f'Firmware actualizado en {updated_count} dispositivos',
                'updated_count': updated_count
            })
        
        elif action_type == 'change_status':
            new_status = request.data.get('status')
            if not new_status:
                return Response({'error': 'status requerido'}, status=400)
            
            updated_count = devices.update(status=new_status)
            
            return Response({
                'success': True,
                'message': f'Estado actualizado en {updated_count} dispositivos',
                'updated_count': updated_count
            })
        
        return Response({'error': 'Acción no válida'}, status=400)

class IoTNetworkHealthView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user_devices = IoTDevice.objects.filter(owner=request.user)
        
        network_health = {
            'total_devices': user_devices.count(),
            'online_devices': user_devices.filter(status='ACTIVE').count(),
            'offline_devices': user_devices.filter(status='INACTIVE').count(),
            'devices_needing_attention': user_devices.filter(
                Q(battery_level__lt=20) | 
                Q(status='MAINTENANCE')
            ).count(),
            'avg_battery_level': user_devices.aggregate(avg=Avg('battery_level'))['avg'] or 0,
            'connectivity_score': self.calculate_connectivity_score(user_devices)
        }
        
        return Response(network_health)
    
    def calculate_connectivity_score(self, devices):
        # Lógica simplificada para score de conectividad
        online_count = devices.filter(status='ACTIVE').count()
        total_count = devices.count()
        
        if total_count == 0:
            return 0
        
        return (online_count / total_count) * 100

class PredictiveMaintenanceView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user_devices = IoTDevice.objects.filter(owner=request.user)
        
        maintenance_predictions = []
        
        for device in user_devices:
            prediction = self.predict_maintenance(device)
            if prediction['needs_maintenance']:
                maintenance_predictions.append(prediction)
        
        return Response({
            'predictions': maintenance_predictions,
            'total_predictions': len(maintenance_predictions)
        })
    
    def predict_maintenance(self, device):
        # Lógica simplificada de predicción
        needs_maintenance = (
            device.battery_level < 15 or
            (timezone.now() - device.last_reading).days > 7
        )
        
        return {
            'device_id': device.device_id,
            'device_name': device.name,
            'needs_maintenance': needs_maintenance,
            'reasons': [
                'Batería baja' if device.battery_level < 15 else None,
                'Sin comunicación reciente' if (timezone.now() - device.last_reading).days > 7 else None
            ]
        }
