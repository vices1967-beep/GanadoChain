from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from .models import IoTDevice, GPSData, HealthSensorData
from .serializers import (
    IoTDeviceSerializer, GPSDataSerializer, 
    HealthSensorDataSerializer, IoTDataIngestSerializer
)
from .permissions import IsDeviceOwner, IsIoTDevice

class IoTDeviceListCreateView(generics.ListCreateAPIView):
    serializer_class = IoTDeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return IoTDevice.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class IoTDeviceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = IoTDeviceSerializer
    permission_classes = [permissions.IsAuthenticated, IsDeviceOwner]

    def get_queryset(self):
        return IoTDevice.objects.filter(owner=self.request.user)

class GPSDataListView(generics.ListAPIView):
    serializer_class = GPSDataSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        animal_id = self.request.query_params.get('animal_id')
        queryset = GPSData.objects.filter(animal__owner=self.request.user)
        
        if animal_id:
            queryset = queryset.filter(animal_id=animal_id)
        
        return queryset.order_by('-timestamp')

class HealthDataListView(generics.ListAPIView):
    serializer_class = HealthSensorDataSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        animal_id = self.request.query_params.get('animal_id')
        queryset = HealthSensorData.objects.filter(animal__owner=self.request.user)
        
        if animal_id:
            queryset = queryset.filter(animal_id=animal_id)
        
        return queryset.order_by('-timestamp')

class IoTDataIngestView(APIView):
    permission_classes = [IsIoTDevice]
    
    def post(self, request):
        serializer = IoTDataIngestSerializer(data=request.data)
        if serializer.is_valid():
            device = request.device  # Set by IsIoTDevice permission
            
            # Procesar datos GPS
            if 'gps_data' in serializer.validated_data:
                gps_data = serializer.validated_data['gps_data']
                GPSData.objects.create(
                    device=device,
                    animal_id=gps_data['animal_id'],
                    latitude=gps_data['latitude'],
                    longitude=gps_data['longitude'],
                    altitude=gps_data.get('altitude'),
                    accuracy=gps_data.get('accuracy'),
                    speed=gps_data.get('speed'),
                    timestamp=timezone.now()
                )
            
            # Procesar datos de salud
            if 'health_data' in serializer.validated_data:
                health_data = serializer.validated_data['health_data']
                HealthSensorData.objects.create(
                    device=device,
                    animal_id=health_data['animal_id'],
                    heart_rate=health_data.get('heart_rate'),
                    temperature=health_data.get('temperature'),
                    activity_level=health_data.get('activity_level'),
                    rumination_time=health_data.get('rumination_time'),
                    feeding_activity=health_data.get('feeding_activity'),
                    timestamp=timezone.now()
                )
            
            # Actualizar último visto del dispositivo
            device.last_seen = timezone.now()
            device.save()
            
            return Response({'status': 'success'}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)