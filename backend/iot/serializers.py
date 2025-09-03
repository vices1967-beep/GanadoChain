from rest_framework import serializers
from .models import IoTDevice, GPSData, HealthSensorData, DeviceEvent, DeviceConfiguration
from .analytics_models import DeviceAnalytics
from cattle.models import Animal
from cattle.serializers import AnimalSerializer
import re
from decimal import Decimal

class IoTDeviceSerializer(serializers.ModelSerializer):
    device_type_display = serializers.CharField(source='get_device_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    battery_status = serializers.CharField(read_only=True)
    last_reading_ago = serializers.CharField(read_only=True)
    animal_ear_tag = serializers.CharField(source='animal.ear_tag', read_only=True, allow_null=True)
    animal_breed = serializers.CharField(source='animal.breed', read_only=True, allow_null=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    
    class Meta:
        model = IoTDevice
        fields = [
            'id', 'device_id', 'device_type', 'device_type_display', 'name',
            'description', 'status', 'status_display', 'is_active', 'animal',
            'animal_ear_tag', 'animal_breed', 'owner', 'owner_name', 'owner_email',
            'firmware_version', 'battery_level', 'battery_status', 'last_reading',
            'last_reading_ago', 'location', 'ip_address', 'mac_address',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_active', 'battery_status', 'last_reading_ago']
    
    def validate_mac_address(self, value):
        if value and not re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', value):
            raise serializers.ValidationError('Formato de MAC address inválido')
        return value
    
    def validate_device_id(self, value):
        # Validar que el device_id sea único
        if IoTDevice.objects.filter(device_id=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError('Ya existe un dispositivo con este ID')
        return value

class GPSDataSerializer(serializers.ModelSerializer):
    device_id = serializers.CharField(source='device.device_id', read_only=True)
    animal_ear_tag = serializers.CharField(source='animal.ear_tag', read_only=True)
    google_maps_url = serializers.CharField(read_only=True)
    is_accurate = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = GPSData
        fields = [
            'id', 'device', 'device_id', 'animal', 'animal_ear_tag', 'latitude',
            'longitude', 'altitude', 'accuracy', 'speed', 'heading', 'satellites',
            'hdop', 'timestamp', 'recorded_at', 'blockchain_hash', 'google_maps_url',
            'is_accurate'
        ]
        read_only_fields = ['recorded_at', 'blockchain_hash', 'google_maps_url', 'is_accurate']
    
    def validate_latitude(self, value):
        if value < -90 or value > 90:
            raise serializers.ValidationError('La latitud debe estar entre -90 y 90')
        return value
    
    def validate_longitude(self, value):
        if value < -180 or value > 180:
            raise serializers.ValidationError('La longitud debe estar entre -180 y 180')
        return value

class HealthSensorDataSerializer(serializers.ModelSerializer):
    device_id = serializers.CharField(source='device.device_id', read_only=True)
    animal_ear_tag = serializers.CharField(source='animal.ear_tag', read_only=True)
    has_anomalies = serializers.ListField(read_only=True)
    health_status = serializers.CharField(read_only=True)
    health_status_display = serializers.CharField(source='get_health_status_display', read_only=True)
    
    class Meta:
        model = HealthSensorData
        fields = [
            'id', 'device', 'device_id', 'animal', 'animal_ear_tag', 'heart_rate',
            'temperature', 'movement_activity', 'rumination_time', 'feeding_activity',
            'respiratory_rate', 'posture', 'ambient_temperature', 'humidity',
            'timestamp', 'recorded_at', 'blockchain_hash', 'processed', 'health_alert',
            'has_anomalies', 'health_status', 'health_status_display'
        ]
        read_only_fields = [
            'recorded_at', 'blockchain_hash', 'processed', 'health_alert',
            'has_anomalies', 'health_status', 'health_status_display'
        ]
    
    def validate_heart_rate(self, value):
        if value and (value < 30 or value > 200):
            raise serializers.ValidationError('El ritmo cardíaco debe estar entre 30 y 200 BPM')
        return value
    
    def validate_temperature(self, value):
        if value and (value < Decimal('35.0') or value > Decimal('42.0')):
            raise serializers.ValidationError('La temperatura debe estar entre 35.0 y 42.0 °C')
        return value

class DeviceEventSerializer(serializers.ModelSerializer):
    device_id = serializers.CharField(source='device.device_id', read_only=True)
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    resolved_by_name = serializers.CharField(source='resolved_by.get_full_name', read_only=True, allow_null=True)
    data_prettified = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = DeviceEvent
        fields = [
            'id', 'device', 'device_id', 'event_type', 'event_type_display',
            'severity', 'severity_display', 'message', 'data', 'data_prettified',
            'resolved', 'resolved_at', 'resolved_by', 'resolved_by_name',
            'timestamp', 'created_at'
        ]
        read_only_fields = ['created_at', 'data_prettified']
    
    def get_data_prettified(self, obj):
        import json
        return json.dumps(obj.data, indent=2, ensure_ascii=False)

class DeviceConfigurationSerializer(serializers.ModelSerializer):
    device_id = serializers.CharField(source='device.device_id', read_only=True)
    device_name = serializers.CharField(source='device.name', read_only=True)
    
    class Meta:
        model = DeviceConfiguration
        fields = [
            'id', 'device', 'device_id', 'device_name', 'sampling_interval',
            'data_retention', 'alert_thresholds', 'gps_enabled', 'health_monitoring',
            'low_power_mode', 'firmware_auto_update', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class DeviceAnalyticsSerializer(serializers.ModelSerializer):
    device_id = serializers.CharField(source='device.device_id', read_only=True)
    device_name = serializers.CharField(source='device.name', read_only=True)
    
    class Meta:
        model = DeviceAnalytics
        fields = [
            'id', 'device', 'device_id', 'device_name', 'date', 'total_readings',
            'avg_battery_level', 'connectivity_uptime', 'data_quality_score',
            'alerts_triggered', 'created_at'
        ]
        read_only_fields = ['created_at']

class GPSDataIngestSerializer(serializers.Serializer):
    device_id = serializers.CharField(max_length=100)
    animal_ear_tag = serializers.CharField(max_length=100)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    altitude = serializers.DecimalField(max_digits=6, decimal_places=2, required=False, allow_null=True)
    accuracy = serializers.DecimalField(max_digits=6, decimal_places=2, required=False, allow_null=True)
    speed = serializers.DecimalField(max_digits=6, decimal_places=2, required=False, allow_null=True)
    heading = serializers.DecimalField(max_digits=5, decimal_places=2, required=False, allow_null=True)
    satellites = serializers.IntegerField(required=False, allow_null=True)
    hdop = serializers.DecimalField(max_digits=4, decimal_places=2, required=False, allow_null=True)
    timestamp = serializers.DateTimeField(required=False)
    
    def validate_latitude(self, value):
        if value < -90 or value > 90:
            raise serializers.ValidationError('La latitud debe estar entre -90 y 90')
        return value
    
    def validate_longitude(self, value):
        if value < -180 or value > 180:
            raise serializers.ValidationError('La longitud debe estar entre -180 y 180')
        return value

class HealthDataIngestSerializer(serializers.Serializer):
    device_id = serializers.CharField(max_length=100)
    animal_ear_tag = serializers.CharField(max_length=100)
    heart_rate = serializers.IntegerField(required=False, allow_null=True, min_value=30, max_value=200)
    temperature = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False, allow_null=True,
        min_value=Decimal('35.0'), max_value=Decimal('42.0')
    )
    movement_activity = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False, allow_null=True,
        min_value=Decimal('0'), max_value=Decimal('100')
    )
    rumination_time = serializers.IntegerField(required=False, allow_null=True, min_value=0, max_value=1440)
    feeding_activity = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False, allow_null=True,
        min_value=Decimal('0'), max_value=Decimal('100')
    )
    respiratory_rate = serializers.IntegerField(required=False, allow_null=True, min_value=5, max_value=50)
    posture = serializers.CharField(required=False, allow_blank=True, max_length=50)
    ambient_temperature = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False, allow_null=True,
        min_value=Decimal('-20'), max_value=Decimal('60')
    )
    humidity = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False, allow_null=True,
        min_value=Decimal('0'), max_value=Decimal('100')
    )
    timestamp = serializers.DateTimeField(required=False)
    
    def validate(self, data):
        # Al menos un dato de salud debe ser proporcionado
        health_fields = ['heart_rate', 'temperature', 'movement_activity', 'rumination_time', 
                        'feeding_activity', 'respiratory_rate', 'posture']
        if not any(field in data for field in health_fields):
            raise serializers.ValidationError('Al menos un dato de salud debe ser proporcionado')
        return data

class IoTDataIngestSerializer(serializers.Serializer):
    gps_data = GPSDataIngestSerializer(required=False)
    health_data = HealthDataIngestSerializer(required=False)
    device_info = serializers.JSONField(required=False)
    
    def validate(self, data):
        if not data.get('gps_data') and not data.get('health_data'):
            raise serializers.ValidationError('Se requiere al menos gps_data o health_data')
        return data

class DeviceStatusUpdateSerializer(serializers.Serializer):
    device_id = serializers.CharField(max_length=100)
    status = serializers.ChoiceField(choices=IoTDevice.DEVICE_STATUS)
    battery_level = serializers.IntegerField(required=False, min_value=0, max_value=100)
    firmware_version = serializers.CharField(required=False, max_length=50)
    ip_address = serializers.IPAddressField(required=False)
    message = serializers.CharField(required=False, max_length=500)

class BulkDataIngestSerializer(serializers.Serializer):
    gps_data = GPSDataIngestSerializer(many=True, required=False)
    health_data = HealthDataIngestSerializer(many=True, required=False)
    
    def validate(self, data):
        if not data.get('gps_data') and not data.get('health_data'):
            raise serializers.ValidationError('Se requiere al menos gps_data o health_data')
        return data

class AlertThresholdSerializer(serializers.Serializer):
    heart_rate_min = serializers.IntegerField(default=40, min_value=30, max_value=60)
    heart_rate_max = serializers.IntegerField(default=100, min_value=80, max_value=120)
    temperature_min = serializers.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('37.5'), 
        min_value=Decimal('35.0'), max_value=Decimal('38.0')
    )
    temperature_max = serializers.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('39.5'), 
        min_value=Decimal('39.0'), max_value=Decimal('42.0')
    )
    respiratory_rate_min = serializers.IntegerField(default=10, min_value=5, max_value=15)
    respiratory_rate_max = serializers.IntegerField(default=30, min_value=25, max_value=40)
    movement_threshold = serializers.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('20.0'), 
        min_value=Decimal('0'), max_value=Decimal('100')
    )
    battery_threshold = serializers.IntegerField(default=20, min_value=5, max_value=30)

class DeviceRegistrationSerializer(serializers.Serializer):
    device_id = serializers.CharField(max_length=100)
    device_type = serializers.ChoiceField(choices=IoTDevice.DEVICE_TYPES)
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(required=False, allow_blank=True)
    firmware_version = serializers.CharField(default='1.0.0', max_length=50)
    mac_address = serializers.CharField(required=False, allow_blank=True, max_length=17)
    animal_ear_tag = serializers.CharField(required=False, allow_blank=True, max_length=100)
    
    def validate_mac_address(self, value):
        if value and not re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', value):
            raise serializers.ValidationError('Formato de MAC address inválido')
        return value