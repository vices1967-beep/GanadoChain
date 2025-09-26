from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.html import format_html
import re

# ✅ Importar validadores centralizados
from core.models import validate_transaction_hash

User = get_user_model()

class IoTDevice(models.Model):
    DEVICE_TYPES = [
        ('TEMPERATURE', 'Sensor de Temperatura'),
        ('HEART_RATE', 'Sensor de Ritmo Cardíaco'),
        ('MOVEMENT', 'Sensor de Movimiento'),
        ('GPS', 'Sensor de Ubicación'),
        ('MULTI', 'Sensor Multifunción'),
        ('CARAVANA', 'Caravana Inteligente'),
        ('GATEWAY', 'Gateway IoT'),
    ]
    
    DEVICE_STATUS = [
        ('ACTIVE', 'Activo'),
        ('INACTIVE', 'Inactivo'),
        ('MAINTENANCE', 'En Mantenimiento'),
        ('DISCONNECTED', 'Desconectado'),
        ('LOW_BATTERY', 'Batería Baja'),
    ]
    
    device_id = models.CharField(max_length=100, unique=True, verbose_name="ID del Dispositivo")
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPES, verbose_name="Tipo de Dispositivo")
    name = models.CharField(max_length=100, verbose_name="Nombre del Dispositivo")
    description = models.TextField(blank=True, verbose_name="Descripción")
    status = models.CharField(max_length=20, choices=DEVICE_STATUS, default='ACTIVE', verbose_name="Estado")
    animal = models.ForeignKey('cattle.Animal', on_delete=models.SET_NULL, null=True, blank=True, related_name='iot_devices', verbose_name="Animal Asociado")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='iot_devices', verbose_name="Propietario")
    firmware_version = models.CharField(max_length=50, default='1.0.0', verbose_name="Versión de Firmware")
    battery_level = models.IntegerField(null=True, blank=True, verbose_name="Nivel de Batería (%)")
    last_reading = models.DateTimeField(null=True, blank=True, verbose_name="Última Lectura")
    location = models.CharField(max_length=255, blank=True, verbose_name="Ubicación")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Dirección IP")
    mac_address = models.CharField(max_length=17, blank=True, verbose_name="Dirección MAC")
    auth_token = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name="Token de Autenticación",
        help_text="Token para autenticación API de dispositivos"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        verbose_name = "Dispositivo IoT"
        verbose_name_plural = "Dispositivos IoT"
        indexes = [
            models.Index(fields=['device_id']),
            models.Index(fields=['device_type']),
            models.Index(fields=['status']),
            models.Index(fields=['animal']),
            models.Index(fields=['owner']),
            models.Index(fields=['last_reading']),
            models.Index(fields=['auth_token']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.device_id} - {self.name} ({self.get_device_type_display()})"
    
    def clean(self):
        super().clean()
        # Validar formato de MAC address si se proporciona
        if self.mac_address and not re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', self.mac_address):
            raise ValidationError({'mac_address': 'Formato de MAC address inválido'})
        
        # Validar que el auth_token sea único si se proporciona
        if self.auth_token and IoTDevice.objects.filter(auth_token=self.auth_token).exclude(id=self.id).exists():
            raise ValidationError({'auth_token': 'Este token de autenticación ya está en uso'})
    
    def save(self, *args, **kwargs):
        # Generar auth_token automáticamente si no se proporciona
        if not self.auth_token and self.device_id:
            import secrets
            self.auth_token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)
    
    @property
    def is_active(self):
        return self.status == 'ACTIVE'
    
    @property
    def battery_status(self):
        if self.battery_level is None:
            return "Desconocido"
        elif self.battery_level > 70:
            return "Alto"
        elif self.battery_level > 30:
            return "Medio"
        elif self.battery_level > 10:
            return "Bajo"
        else:
            return "Crítico"
    
    @property
    def last_reading_ago(self):
        from django.utils import timezone
        from django.utils.timesince import timesince
        if self.last_reading:
            return timesince(self.last_reading, timezone.now())
        return "Nunca"
    
    def get_absolute_url(self):
        return reverse('admin:iot_iotdevice_change', args=[self.id])
    
class GPSData(models.Model):
    device = models.ForeignKey(IoTDevice, on_delete=models.CASCADE, related_name='gps_data', verbose_name="Dispositivo")
    animal = models.ForeignKey('cattle.Animal', on_delete=models.CASCADE, related_name='gps_data', verbose_name="Animal")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Latitud")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Longitud")
    altitude = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Altitud (m)")
    accuracy = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Precisión (m)")
    speed = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Velocidad (km/h)")
    heading = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Rumbo (°)")
    satellites = models.IntegerField(null=True, blank=True, verbose_name="Satélites")
    hdop = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="HDOP")
    timestamp = models.DateTimeField(verbose_name="Timestamp del Dispositivo")
    recorded_at = models.DateTimeField(auto_now_add=True, verbose_name="Registrado el")
    
    # ✅ CAMPO BLOCKCHAIN CON VALIDADOR
    blockchain_hash = models.CharField(
        max_length=66, 
        blank=True, 
        null=True, 
        verbose_name="Hash Blockchain",
        validators=[validate_transaction_hash]  # ✅ VALIDADOR AÑADIDO
    )

    class Meta:
        verbose_name = "Datos GPS"
        verbose_name_plural = "Datos GPS"
        indexes = [
            models.Index(fields=['animal', 'timestamp']),
            models.Index(fields=['device', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]
        ordering = ['-timestamp']

    def __str__(self):
        return f"GPS {self.device.device_id} - {self.timestamp}"
    
    @property
    def google_maps_url(self):
        return f"https://www.google.com/maps?q={self.latitude},{self.longitude}"
    
    @property
    def is_accurate(self):
        return self.accuracy is not None and self.accuracy <= 10.0
    
    def clean(self):
        super().clean()
        if self.latitude < -90 or self.latitude > 90:
            raise ValidationError({'latitude': 'La latitud debe estar entre -90 y 90'})
        if self.longitude < -180 or self.longitude > 180:
            raise ValidationError({'longitude': 'La longitud debe estar entre -180 y 180'})
    
    def save(self, *args, **kwargs):
        # Normalizar hash antes de guardar
        if self.blockchain_hash and not self.blockchain_hash.startswith('0x'):
            self.blockchain_hash = '0x' + self.blockchain_hash
        super().save(*args, **kwargs)

class HealthSensorData(models.Model):
    device = models.ForeignKey(IoTDevice, on_delete=models.CASCADE, related_name='health_data', verbose_name="Dispositivo")
    animal = models.ForeignKey('cattle.Animal', on_delete=models.CASCADE, related_name='health_data', verbose_name="Animal")
    heart_rate = models.IntegerField(null=True, blank=True, verbose_name="Ritmo Cardíaco (BPM)")
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Temperatura (°C)")
    movement_activity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Actividad de Movimiento")
    rumination_time = models.IntegerField(null=True, blank=True, verbose_name="Tiempo de Rumia (min)")
    feeding_activity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Actividad de Alimentación")
    respiratory_rate = models.IntegerField(null=True, blank=True, verbose_name="Ritmo Respiratorio")
    posture = models.CharField(max_length=50, blank=True, verbose_name="Postura")
    ambient_temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Temperatura Ambiental (°C)")
    humidity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Humedad (%)")
    timestamp = models.DateTimeField(verbose_name="Timestamp del Dispositivo")
    recorded_at = models.DateTimeField(auto_now_add=True, verbose_name="Registrado el")
    
    # ✅ CAMPO BLOCKCHAIN CON VALIDADOR
    blockchain_hash = models.CharField(
        max_length=66, 
        blank=True, 
        null=True, 
        verbose_name="Hash Blockchain",
        validators=[validate_transaction_hash]  # ✅ VALIDADOR AÑADIDO
    )
    processed = models.BooleanField(default=False, verbose_name="Procesado")
    health_alert = models.BooleanField(default=False, verbose_name="Alerta de Salud")

    class Meta:
        verbose_name = "Datos de Salud"
        verbose_name_plural = "Datos de Salud"
        indexes = [
            models.Index(fields=['animal', 'timestamp']),
            models.Index(fields=['device', 'timestamp']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['health_alert']),
            models.Index(fields=['processed']),
        ]
        ordering = ['-timestamp']

    def __str__(self):
        return f"Salud {self.device.device_id} - {self.timestamp}"
    
    @property
    def has_anomalies(self):
        """Detectar anomalías en los datos de salud"""
        anomalies = []
        if self.heart_rate and (self.heart_rate < 40 or self.heart_rate > 100):
            anomalies.append('ritmo_cardíaco')
        if self.temperature and (self.temperature < 37.5 or self.temperature > 39.5):
            anomalies.append('temperatura')
        if self.respiratory_rate and (self.respiratory_rate < 10 or self.respiratory_rate > 30):
            anomalies.append('ritmo_respiratorio')
        return anomalies
    
    @property
    def health_status(self):
        """Determinar estado de salud basado en los datos"""
        from cattle.models import HealthStatus
        
        anomalies = self.has_anomalies
        if not anomalies:
            return HealthStatus.HEALTHY
        elif 'temperatura' in anomalies and self.temperature > 39.5:
            return HealthStatus.SICK
        elif len(anomalies) >= 2:
            return HealthStatus.UNDER_OBSERVATION
        else:
            return HealthStatus.HEALTHY
    
    def save(self, *args, **kwargs):
        # Normalizar hash antes de guardar
        if self.blockchain_hash and not self.blockchain_hash.startswith('0x'):
            self.blockchain_hash = '0x' + self.blockchain_hash
        super().save(*args, **kwargs)

class DeviceEvent(models.Model):
    EVENT_TYPES = [
        ('CONNECT', 'Conexión'),
        ('DISCONNECT', 'Desconexión'),
        ('LOW_BATTERY', 'Batería Baja'),
        ('MAINTENANCE', 'Mantenimiento'),
        ('ERROR', 'Error'),
        ('FIRMWARE_UPDATE', 'Actualización de Firmware'),
        ('LOCATION_UPDATE', 'Actualización de Ubicación'),
        ('HEALTH_ALERT', 'Alerta de Salud'),
    ]
    
    SEVERITY_LEVELS = [
        ('LOW', 'Bajo'),
        ('MEDIUM', 'Medio'),
        ('HIGH', 'Alto'),
        ('CRITICAL', 'Crítico'),
    ]
    
    device = models.ForeignKey(IoTDevice, on_delete=models.CASCADE, related_name='events', verbose_name="Dispositivo")
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, verbose_name="Tipo de Evento")
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default='LOW', verbose_name="Severidad")
    message = models.TextField(verbose_name="Mensaje")
    data = models.JSONField(default=dict, blank=True, verbose_name="Datos Adicionales")
    resolved = models.BooleanField(default=False, verbose_name="Resuelto")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="Resuelto el")
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Resuelto por")
    timestamp = models.DateTimeField(verbose_name="Timestamp del Evento")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado el")

    class Meta:
        verbose_name = "Evento de Dispositivo"
        verbose_name_plural = "Eventos de Dispositivo"
        indexes = [
            models.Index(fields=['device', 'timestamp']),
            models.Index(fields=['event_type']),
            models.Index(fields=['severity']),
            models.Index(fields=['resolved']),
        ]
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.device.device_id} - {self.get_event_type_display()} - {self.timestamp}"

class DeviceConfiguration(models.Model):
    device = models.OneToOneField(IoTDevice, on_delete=models.CASCADE, related_name='configuration', verbose_name="Dispositivo")
    sampling_interval = models.IntegerField(default=300, verbose_name="Intervalo de Muestreo (s)")
    data_retention = models.IntegerField(default=30, verbose_name="Retención de Datos (días)")
    alert_thresholds = models.JSONField(default=dict, verbose_name="Umbrales de Alerta")
    gps_enabled = models.BooleanField(default=True, verbose_name="GPS Habilitado")
    health_monitoring = models.BooleanField(default=True, verbose_name="Monitoreo de Salud")
    low_power_mode = models.BooleanField(default=False, verbose_name="Modo Bajo Consumo")
    firmware_auto_update = models.BooleanField(default=False, verbose_name="Actualización Automática")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado el")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado el")

    class Meta:
        verbose_name = "Configuración de Dispositivo"
        verbose_name_plural = "Configuraciones de Dispositivo"

    def __str__(self):
        return f"Configuración de {self.device.device_id}"
    
    @property
    def owner(self):
        """Propiedad para compatibilidad con permisos"""
        return self.device.owner if self.device else None
    
    from .multichain_models import IoTDeviceMultichain, SensorDataMultichain, DeviceEventMultichain, GatewayDevice