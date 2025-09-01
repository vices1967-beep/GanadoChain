from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class IoTDevice(models.Model):
    DEVICE_TYPES = [
        ('GPS', 'Dispositivo GPS'),
        ('SENSOR', 'Sensor de Salud'),
        ('CARAVANA', 'Caravana Inteligente'),
        ('GATEWAY', 'Gateway IoT'),
    ]
    
    device_id = models.CharField(max_length=100, unique=True)
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPES)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    installed_on = models.ForeignKey('cattle.Animal', on_delete=models.CASCADE, null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    firmware_version = models.CharField(max_length=50, default='1.0.0')
    last_seen = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Dispositivo IoT"
        verbose_name_plural = "Dispositivos IoT"

class GPSData(models.Model):
    device = models.ForeignKey(IoTDevice, on_delete=models.CASCADE)
    animal = models.ForeignKey('cattle.Animal', on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    altitude = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    accuracy = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    speed = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    timestamp = models.DateTimeField()
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Datos GPS"
        verbose_name_plural = "Datos GPS"
        indexes = [
            models.Index(fields=['animal', 'timestamp']),
            models.Index(fields=['device', 'timestamp']),
        ]

class HealthSensorData(models.Model):
    device = models.ForeignKey(IoTDevice, on_delete=models.CASCADE)
    animal = models.ForeignKey('cattle.Animal', on_delete=models.CASCADE)
    heart_rate = models.IntegerField(null=True, blank=True)  # BPM
    temperature = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)  # °C
    activity_level = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # %
    rumination_time = models.IntegerField(null=True, blank=True)  # minutos
    feeding_activity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    timestamp = models.DateTimeField()
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Datos de Salud"
        verbose_name_plural = "Datos de Salud"