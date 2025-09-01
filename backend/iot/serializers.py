from rest_framework import serializers
from .models import IoTDevice, GPSData, HealthSensorData

class IoTDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = IoTDevice
        fields = '__all__'
        read_only_fields = ('owner', 'last_seen', 'created_at')

class GPSDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPSData
        fields = '__all__'

class HealthSensorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthSensorData
        fields = '__all__'

class GPSDataIngestSerializer(serializers.Serializer):
    animal_id = serializers.IntegerField()
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    altitude = serializers.DecimalField(max_digits=6, decimal_places=2, required=False)
    accuracy = serializers.DecimalField(max_digits=6, decimal_places=2, required=False)
    speed = serializers.DecimalField(max_digits=6, decimal_places=2, required=False)

class HealthDataIngestSerializer(serializers.Serializer):
    animal_id = serializers.IntegerField()
    heart_rate = serializers.IntegerField(required=False)
    temperature = serializers.DecimalField(max_digits=4, decimal_places=2, required=False)
    activity_level = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    rumination_time = serializers.IntegerField(required=False)
    feeding_activity = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)

class IoTDataIngestSerializer(serializers.Serializer):
    gps_data = GPSDataIngestSerializer(required=False)
    health_data = HealthDataIngestSerializer(required=False)