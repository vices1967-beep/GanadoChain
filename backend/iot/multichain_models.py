# backend/iot/multichain_models.py
from django.db import models
from django.core.exceptions import ValidationError
from core.multichain.models import BlockchainNetwork, ChainSpecificModel
from core.multichain.manager import multichain_manager
import secrets
import json

class IoTDeviceMultichain(models.Model):
    """Dispositivo IoT con capacidades multichain"""
    DEVICE_TYPES = [
        ('CARAVANA', 'Caravana Inteligente'),
        ('SENSOR_GPS', 'Sensor GPS'),
        ('SENSOR_TEMPERATURA', 'Sensor de Temperatura'),
        ('SENSOR_CARDIACO', 'Sensor Cardíaco'),
        ('SENSOR_MOVIMIENTO', 'Sensor de Movimiento'),
        ('GATEWAY', 'Gateway IoT'),
        ('DRONE', 'Dron de Monitoreo'),
    ]
    
    DEVICE_STATUS = [
        ('ACTIVE', 'Activo'),
        ('INACTIVE', 'Inactivo'),
        ('CALIBRATING', 'Calibrando'),
        ('MAINTENANCE', 'En Mantenimiento'),
        ('OFFLINE', 'Desconectado'),
        ('LOW_BATTERY', 'Batería Baja'),
    ]
    
    # Identificación única
    device_id = models.CharField(max_length=100, unique=True, verbose_name="ID del Dispositivo")
    serial_number = models.CharField(max_length=100, unique=True, verbose_name="Número de Serie")
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPES, verbose_name="Tipo de Dispositivo")
    
    # Propietario y ubicación - CORREGIDO: related_name únicos
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='multichain_iot_devices')
    animal = models.ForeignKey('cattle.Animal', on_delete=models.SET_NULL, null=True, blank=True, 
                              related_name='multichain_iot_devices', verbose_name="Animal Asociado")
    current_location = models.CharField(max_length=255, blank=True, verbose_name="Ubicación Actual")
    
    # Estado del dispositivo
    status = models.CharField(max_length=15, choices=DEVICE_STATUS, default='ACTIVE', verbose_name="Estado")
    battery_level = models.IntegerField(null=True, blank=True, verbose_name="Nivel de Batería (%)")
    signal_strength = models.IntegerField(null=True, blank=True, verbose_name="Intensidad de Señal")
    
    # Configuración multichain
    preferred_network = models.ForeignKey(
        BlockchainNetwork, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="Red Preferida"
    )
    blockchain_registered = models.BooleanField(default=False, verbose_name="Registrado en Blockchain")
    blockchain_device_id = models.CharField(max_length=255, blank=True, verbose_name="ID en Blockchain")
    
    # Seguridad y autenticación
    auth_token = models.CharField(max_length=100, blank=True, verbose_name="Token de Autenticación")
    public_key = models.TextField(blank=True, verbose_name="Clave Pública")
    encrypted_private_key = models.TextField(blank=True, verbose_name="Clave Privada Encriptada")
    
    # Metadata
    firmware_version = models.CharField(max_length=50, default='1.0.0', verbose_name="Versión de Firmware")
    manufacturer = models.CharField(max_length=100, blank=True, verbose_name="Fabricante")
    model = models.CharField(max_length=100, blank=True, verbose_name="Modelo")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_communication = models.DateTimeField(null=True, blank=True, verbose_name="Última Comunicación")

    class Meta:
        verbose_name = "Dispositivo IoT Multichain"
        verbose_name_plural = "Dispositivos IoT Multichain"
        indexes = [
            models.Index(fields=['device_id']),
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['animal', 'device_type']),
            models.Index(fields=['last_communication']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.device_id} - {self.get_device_type_display()} - {self.owner.username}"
    
    def clean(self):
        super().clean()
        if self.battery_level and (self.battery_level < 0 or self.battery_level > 100):
            raise ValidationError({'battery_level': 'El nivel de batería debe estar entre 0 y 100%'})
    
    def save(self, *args, **kwargs):
        # Generar auth_token automáticamente si no existe
        if not self.auth_token:
            self.auth_token = secrets.token_urlsafe(32)
        
        # Generar ID único para blockchain si es necesario
        if not self.blockchain_device_id and self.blockchain_registered:
            self.blockchain_device_id = f"iot_{self.device_id}_{secrets.token_hex(8)}"
            
        super().save(*args, **kwargs)
    
    @property
    def is_online(self):
        """Verificar si el dispositivo está online"""
        from django.utils import timezone
        if self.last_communication:
            return (timezone.now() - self.last_communication).total_seconds() < 300  # 5 minutos
        return False
    
    @property
    def needs_maintenance(self):
        """Verificar si necesita mantenimiento"""
        return self.status in ['LOW_BATTERY', 'CALIBRATING', 'MAINTENANCE']
    
    def register_on_blockchain(self, network_id=None):
        """Registrar dispositivo en blockchain"""
        from .adapters.multichain_adapter import IoTDeviceMultichainAdapter
        adapter = IoTDeviceMultichainAdapter(self)
        return adapter.register_on_blockchain(network_id)

class SensorDataMultichain(models.Model):
    """Datos de sensores con almacenamiento multichain"""
    DATA_TYPES = [
        ('GPS', 'Datos de Ubicación'),
        ('TEMPERATURE', 'Temperatura'),
        ('HEART_RATE', 'Ritmo Cardíaco'),
        ('MOVEMENT', 'Movimiento'),
        ('HUMIDITY', 'Humedad'),
        ('PRESSURE', 'Presión Atmosférica'),
        ('ACCELEROMETER', 'Acelerómetro'),
        ('GYROSCOPE', 'Giroscopio'),
    ]
    
    device = models.ForeignKey(IoTDeviceMultichain, on_delete=models.CASCADE, related_name='sensor_data')
    data_type = models.CharField(max_length=15, choices=DATA_TYPES, verbose_name="Tipo de Dato")
    
    # Datos del sensor (estructura flexible)
    raw_data = models.JSONField(verbose_name="Datos Crudos")
    processed_data = models.JSONField(default=dict, verbose_name="Datos Procesados")
    
    # Metadata de la lectura
    timestamp = models.DateTimeField(verbose_name="Timestamp del Sensor")
    accuracy = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Precisión")
    battery_at_reading = models.IntegerField(null=True, blank=True, verbose_name="Batería al Momento")
    
    # Blockchain integration
    stored_on_blockchain = models.BooleanField(default=False, verbose_name="Almacenado en Blockchain")
    blockchain_networks = models.JSONField(
        default=list,
        verbose_name="Redes Blockchain",
        help_text="Redes donde están almacenados los datos"
    )
    blockchain_hashes = models.JSONField(
        default=dict,
        verbose_name="Hashes Blockchain",
        help_text="Hashes de transacción por red: {'STARKNET': '0x123...', 'POLYGON': '0x456...'}"
    )
    
    # Análisis y alertas
    anomalies_detected = models.JSONField(default=list, verbose_name="Anomalías Detectadas")
    alert_triggered = models.BooleanField(default=False, verbose_name="Alerta Activada")
    processed_by_ai = models.BooleanField(default=False, verbose_name="Procesado por IA")
    
    recorded_at = models.DateTimeField(auto_now_add=True, verbose_name="Registrado el")

    class Meta:
        verbose_name = "Dato de Sensor Multichain"
        verbose_name_plural = "Datos de Sensor Multichain"
        indexes = [
            models.Index(fields=['device', 'timestamp']),
            models.Index(fields=['data_type', 'timestamp']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['alert_triggered']),
        ]
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.device.device_id} - {self.get_data_type_display()} - {self.timestamp}"
    
    @property
    def is_accurate(self):
        """Verificar si los datos son precisos"""
        return self.accuracy is not None and self.accuracy >= 0.8
    
    @property
    def has_anomalies(self):
        """Verificar si tiene anomalías"""
        return len(self.anomalies_detected) > 0
    
    def store_on_blockchain(self, networks=None):
        """Almacenar datos en blockchain"""
        from .adapters.multichain_adapter import SensorDataMultichainAdapter
        adapter = SensorDataMultichainAdapter(self)
        return adapter.store_on_blockchain(networks)

class DeviceEventMultichain(models.Model):
    """Eventos de dispositivos IoT con registro multichain"""
    EVENT_SEVERITY = [
        ('LOW', 'Bajo'),
        ('MEDIUM', 'Medio'),
        ('HIGH', 'Alto'),
        ('CRITICAL', 'Crítico'),
    ]
    
    EVENT_TYPES = [
        ('STATUS_CHANGE', 'Cambio de Estado'),
        ('BATTERY_LOW', 'Batería Baja'),
        ('DISCONNECTED', 'Desconectado'),
        ('TAMPER_DETECTED', 'Manipulación Detectada'),
        ('DATA_ANOMALY', 'Anomalía en Datos'),
        ('MAINTENANCE_REQUIRED', 'Mantenimiento Requerido'),
        ('FIRMWARE_UPDATE', 'Actualización de Firmware'),
    ]
    
    device = models.ForeignKey(IoTDeviceMultichain, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, verbose_name="Tipo de Evento")
    severity = models.CharField(max_length=10, choices=EVENT_SEVERITY, default='LOW', verbose_name="Severidad")
    
    # Información del evento
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descripción")
    event_data = models.JSONField(default=dict, verbose_name="Datos del Evento")
    
    # Blockchain
    logged_on_blockchain = models.BooleanField(default=False, verbose_name="Registrado en Blockchain")
    blockchain_transaction_hash = models.CharField(max_length=255, blank=True, verbose_name="Hash de Transacción")
    
    # Resolución
    resolved = models.BooleanField(default=False, verbose_name="Resuelto")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="Resuelto el")
    resolution_notes = models.TextField(blank=True, verbose_name="Notas de Resolución")
    
    timestamp = models.DateTimeField(verbose_name="Timestamp del Evento")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Evento de Dispositivo Multichain"
        verbose_name_plural = "Eventos de Dispositivo Multichain"
        indexes = [
            models.Index(fields=['device', 'timestamp']),
            models.Index(fields=['event_type', 'severity']),
            models.Index(fields=['resolved']),
        ]
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.device.device_id} - {self.get_event_type_display()} - {self.timestamp}"
    
    @property
    def requires_immediate_action(self):
        """Verificar si requiere acción inmediata"""
        return self.severity in ['HIGH', 'CRITICAL'] and not self.resolved

class GatewayDevice(models.Model):
    """Dispositivos gateway para agregación de datos IoT"""
    gateway_id = models.CharField(max_length=100, unique=True, verbose_name="ID del Gateway")
    name = models.CharField(max_length=200, verbose_name="Nombre del Gateway")
    location = models.CharField(max_length=255, verbose_name="Ubicación")
    
    # Configuración de red
    ip_address = models.GenericIPAddressField(verbose_name="Dirección IP")
    mac_address = models.CharField(max_length=17, verbose_name="Dirección MAC")
    network_type = models.CharField(max_length=20, choices=[
        ('WIFI', 'Wi-Fi'),
        ('ETHERNET', 'Ethernet'),
        ('CELLULAR', 'Cellular'),
        ('SATELLITE', 'Satellite'),
    ], verbose_name="Tipo de Red")
    
    # Dispositivos conectados
    connected_devices = models.ManyToManyField(
        IoTDeviceMultichain, 
        related_name='gateways',
        blank=True,
        verbose_name="Dispositivos Conectados"
    )
    
    # Capacidades
    max_connected_devices = models.IntegerField(default=50, verbose_name="Máximo de Dispositivos")
    data_processing_capability = models.BooleanField(default=True, verbose_name="Procesamiento de Datos")
    blockchain_sync_capability = models.BooleanField(default=True, verbose_name="Sincronización Blockchain")
    
    # Estado
    status = models.CharField(max_length=15, choices=[
        ('ONLINE', 'Online'),
        ('OFFLINE', 'Offline'),
        ('MAINTENANCE', 'En Mantenimiento'),
    ], default='ONLINE', verbose_name="Estado")
    
    created_at = models.DateTimeField(auto_now_add=True)
    last_heartbeat = models.DateTimeField(null=True, blank=True, verbose_name="Último Latido")

    class Meta:
        verbose_name = "Gateway IoT"
        verbose_name_plural = "Gateways IoT"

    def __str__(self):
        return f"{self.gateway_id} - {self.name}"
    
    @property
    def connected_devices_count(self):
        return self.connected_devices.count()
    
    @property
    def is_online(self):
        from django.utils import timezone
        return self.last_heartbeat and (timezone.now() - self.last_heartbeat).total_seconds() < 300