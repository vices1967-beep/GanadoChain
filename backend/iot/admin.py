from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import IoTDevice, GPSData, HealthSensorData, DeviceEvent, DeviceConfiguration
from .analytics_models import DeviceAnalytics
import json

@admin.register(IoTDevice)
class IoTDeviceAdmin(admin.ModelAdmin):
    list_display = [
        'device_id', 'name', 'device_type_display', 'status_display',
        'animal_link', 'battery_display', 'last_reading_ago',
        'owner_link', 'created_at'
    ]
    
    list_filter = [
        'device_type', 'status', 'created_at', 'last_reading'
    ]
    
    search_fields = [
        'device_id', 'name', 'animal__ear_tag', 'owner__username',
        'owner__email', 'firmware_version', 'mac_address'
    ]
    
    readonly_fields = [
        'created_at', 'updated_at', 'last_reading_ago', 'battery_status',
        'is_active', 'animal_link', 'owner_link', 'analytics_link'
    ]
    
    fieldsets = (
        ('Información del Dispositivo', {
            'fields': (
                'device_id', 'name', 'device_type', 'description'
            )
        }),
        ('Estado y Configuración', {
            'fields': (
                'status', 'firmware_version', 'battery_level', 'battery_status',
                'ip_address', 'mac_address'
            )
        }),
        ('Asociaciones', {
            'fields': (
                'animal_link', 'owner_link', 'location'
            )
        }),
        ('Monitoreo', {
            'fields': (
                'last_reading', 'last_reading_ago', 'is_active'
            )
        }),
        ('Analítica', {
            'fields': ('analytics_link',),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': (
                'created_at', 'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def device_type_display(self, obj):
        type_colors = {
            'TEMPERATURE': 'red',
            'HEART_RATE': 'purple',
            'MOVEMENT': 'green',
            'GPS': 'blue',
            'MULTI': 'orange',
            'CARAVANA': 'teal',
            'GATEWAY': 'indigo'
        }
        color = type_colors.get(obj.device_type, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_device_type_display()
        )
    device_type_display.short_description = 'Tipo'
    
    def status_display(self, obj):
        status_colors = {
            'ACTIVE': 'green',
            'INACTIVE': 'gray',
            'MAINTENANCE': 'orange',
            'DISCONNECTED': 'red',
            'LOW_BATTERY': 'yellow'
        }
        color = status_colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">● {}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Estado'
    
    def animal_link(self, obj):
        if obj.animal:
            url = reverse('admin:cattle_animal_change', args=[obj.animal.id])
            return format_html('<a href="{}">{}</a>', url, obj.animal.ear_tag)
        return "—"
    animal_link.short_description = 'Animal'
    
    def owner_link(self, obj):
        if obj.owner:
            url = reverse('admin:auth_user_change', args=[obj.owner.id])
            return format_html('<a href="{}">{}</a>', url, obj.owner.get_full_name() or obj.owner.username)
        return "—"
    owner_link.short_description = 'Propietario'
    
    def battery_display(self, obj):
        if obj.battery_level is None:
            return "—"
        
        if obj.battery_level > 70:
            color = 'green'
        elif obj.battery_level > 30:
            color = 'orange'
        elif obj.battery_level > 10:
            color = 'red'
        else:
            color = 'darkred'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>',
            color, obj.battery_level
        )
    battery_display.short_description = 'Batería'
    
    def last_reading_ago(self, obj):
        from django.utils import timezone
        from django.utils.timesince import timesince
        if obj.last_reading:
            return timesince(obj.last_reading, timezone.now())
        return "Nunca"
    last_reading_ago.short_description = 'Última Lectura'
    
    def analytics_link(self, obj):
        url = reverse('admin:iot_deviceanalytics_changelist') + f'?device__id__exact={obj.id}'
        return format_html('<a href="{}">📊 Ver Métricas Analíticas</a>', url)
    analytics_link.short_description = 'Analítica'

@admin.register(GPSData)
class GPSDataAdmin(admin.ModelAdmin):
    list_display = [
        'device_id', 'animal_link', 'coordinates_display',
        'accuracy_display', 'speed_display', 'timestamp',
        'is_accurate_display', 'google_maps_link', 'blockchain_linked_display'
    ]
    
    list_filter = [
        'device__device_type', 'timestamp', 'recorded_at'
    ]
    
    search_fields = [
        'device__device_id', 'animal__ear_tag', 'animal__breed',
        'blockchain_hash'
    ]
    
    readonly_fields = [
        'recorded_at', 'google_maps_link', 'is_accurate_display',
        'device_link', 'animal_link', 'blockchain_linked_display',
        'polyscan_link'
    ]
    
    fieldsets = (
        ('Información de Ubicación', {
            'fields': (
                'device_link', 'animal_link', 'latitude', 'longitude'
            )
        }),
        ('Datos Técnicos GPS', {
            'fields': (
                'altitude', 'accuracy', 'speed', 'heading',
                'satellites', 'hdop'
            )
        }),
        ('Metadata', {
            'fields': (
                'timestamp', 'recorded_at'
            )
        }),
        ('Blockchain', {
            'fields': (
                'blockchain_hash', 'blockchain_linked_display', 'polyscan_link'
            ),
            'classes': ('collapse',)
        }),
        ('Visualización', {
            'fields': (
                'google_maps_link', 'is_accurate_display'
            )
        }),
    )
    
    def device_id(self, obj):
        return obj.device.device_id
    device_id.short_description = 'Dispositivo'
    
    def animal_link(self, obj):
        if obj.animal:
            url = reverse('admin:cattle_animal_change', args=[obj.animal.id])
            return format_html('<a href="{}">{}</a>', url, obj.animal.ear_tag)
        return "—"
    animal_link.short_description = 'Animal'
    
    def device_link(self, obj):
        if obj.device:
            url = reverse('admin:iot_iotdevice_change', args=[obj.device.id])
            return format_html('<a href="{}">{}</a>', url, obj.device.device_id)
        return "—"
    device_link.short_description = 'Dispositivo'
    
    def coordinates_display(self, obj):
        return f"{obj.latitude:.6f}, {obj.longitude:.6f}"
    coordinates_display.short_description = 'Coordenadas'
    
    def accuracy_display(self, obj):
        if obj.accuracy:
            color = 'green' if obj.accuracy <= 10.0 else 'orange' if obj.accuracy <= 30.0 else 'red'
            return format_html(
                '<span style="color: {};">{} m</span>',
                color, obj.accuracy
            )
        return "—"
    accuracy_display.short_description = 'Precisión'
    
    def speed_display(self, obj):
        if obj.speed:
            return f"{obj.speed} km/h"
        return "—"
    speed_display.short_description = 'Velocidad'
    
    def is_accurate_display(self, obj):
        if obj.is_accurate:
            return format_html('<span style="color: green;">✅ Precisa</span>')
        return format_html('<span style="color: red;">❌ Imprecisa</span>')
    is_accurate_display.short_description = 'Precisión'
    
    def google_maps_link(self, obj):
        if obj.google_maps_url:
            return format_html(
                '<a href="{}" target="_blank" style="background-color: #4285F4; color: white; padding: 2px 6px; border-radius: 4px; text-decoration: none;">🗺️ Ver en Maps</a>',
                obj.google_maps_url
            )
        return "—"
    google_maps_link.short_description = 'Google Maps'
    
    def blockchain_linked_display(self, obj):
        if obj.blockchain_hash:
            return format_html('<span style="color: green;">✅ Sí</span>')
        return format_html('<span style="color: red;">❌ No</span>')
    blockchain_linked_display.short_description = 'En Blockchain'
    
    def polyscan_link(self, obj):
        if obj.blockchain_hash:
            url = f"https://amoy.polygonscan.com/tx/{obj.blockchain_hash}"
            return format_html('<a href="{}" target="_blank">🔗 Ver en PolyScan</a>', url)
        return "—"
    polyscan_link.short_description = 'Transacción'

@admin.register(HealthSensorData)
class HealthSensorDataAdmin(admin.ModelAdmin):
    list_display = [
        'device_id', 'animal_link', 'temperature_display',
        'heart_rate_display', 'movement_display', 'timestamp',
        'health_alert_display', 'has_anomalies_display', 'blockchain_linked_display'
    ]
    
    list_filter = [
        'health_alert', 'processed', 'timestamp'
    ]
    
    search_fields = [
        'device__device_id', 'animal__ear_tag', 'animal__breed',
        'blockchain_hash'
    ]
    
    readonly_fields = [
        'recorded_at', 'has_anomalies_display', 'health_status_display',
        'device_link', 'animal_link', 'anomalies_list',
        'blockchain_linked_display', 'polyscan_link'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'device_link', 'animal_link', 'timestamp', 'recorded_at'
            )
        }),
        ('Datos Vitales', {
            'fields': (
                'heart_rate', 'temperature', 'respiratory_rate'
            )
        }),
        ('Actividad y Comportamiento', {
            'fields': (
                'movement_activity', 'rumination_time', 'feeding_activity',
                'posture'
            )
        }),
        ('Condiciones Ambientales', {
            'fields': (
                'ambient_temperature', 'humidity'
            )
        }),
        ('Estado y Alertas', {
            'fields': (
                'health_status_display', 'health_alert', 'has_anomalies_display',
                'anomalies_list', 'processed'
            )
        }),
        ('Blockchain', {
            'fields': (
                'blockchain_hash', 'blockchain_linked_display', 'polyscan_link'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def device_id(self, obj):
        return obj.device.device_id
    device_id.short_description = 'Dispositivo'
    
    def animal_link(self, obj):
        if obj.animal:
            url = reverse('admin:cattle_animal_change', args=[obj.animal.id])
            return format_html('<a href="{}">{}</a>', url, obj.animal.ear_tag)
        return "—"
    animal_link.short_description = 'Animal'
    
    def device_link(self, obj):
        if obj.device:
            url = reverse('admin:iot_iotdevice_change', args=[obj.device.id])
            return format_html('<a href="{}">{}</a>', url, obj.device.device_id)
        return "—"
    device_link.short_description = 'Dispositivo'
    
    def temperature_display(self, obj):
        if obj.temperature:
            color = 'green' if 37.5 <= obj.temperature <= 39.5 else 'red'
            return format_html(
                '<span style="color: {};">{}°C</span>',
                color, obj.temperature
            )
        return "—"
    temperature_display.short_description = 'Temperatura'
    
    def heart_rate_display(self, obj):
        if obj.heart_rate:
            color = 'green' if 40 <= obj.heart_rate <= 70 else 'orange' if 30 <= obj.heart_rate <= 100 else 'red'
            return format_html(
                '<span style="color: {};">{} bpm</span>',
                color, obj.heart_rate
            )
        return "—"
    heart_rate_display.short_description = 'Ritmo Cardíaco'
    
    def movement_display(self, obj):
        if obj.movement_activity:
            return f"{obj.movement_activity}%"
        return "—"
    movement_display.short_description = 'Movimiento'
    
    def health_alert_display(self, obj):
        if obj.health_alert:
            return format_html('<span style="color: red;">⚠️ Alerta</span>')
        return format_html('<span style="color: green;">✅ Normal</span>')
    health_alert_display.short_description = 'Alerta'
    
    def has_anomalies_display(self, obj):
        anomalies = obj.has_anomalies
        if anomalies:
            return format_html('<span style="color: orange;">⚠️ {} anomalías</span>', len(anomalies))
        return format_html('<span style="color: green;">✅ Normal</span>')
    has_anomalies_display.short_description = 'Anomalías'
    
    def health_status_display(self, obj):
        status_colors = {
            'HEALTHY': 'green',
            'SICK': 'red',
            'RECOVERING': 'orange',
            'UNDER_OBSERVATION': 'blue',
            'QUARANTINED': 'purple'
        }
        color = status_colors.get(obj.health_status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_health_status_display()
        )
    health_status_display.short_description = 'Estado Salud'
    
    def anomalies_list(self, obj):
        anomalies = obj.has_anomalies
        if anomalies:
            return format_html('<ul>{}</ul>', 
                              ''.join(f'<li>{anom.replace("_", " ").title()}</li>' for anom in anomalies))
        return "No hay anomalías"
    anomalies_list.short_description = 'Anomalías Detectadas'
    
    def blockchain_linked_display(self, obj):
        if obj.blockchain_hash:
            return format_html('<span style="color: green;">✅ Sí</span>')
        return format_html('<span style="color: red;">❌ No</span>')
    blockchain_linked_display.short_description = 'En Blockchain'
    
    def polyscan_link(self, obj):
        if obj.blockchain_hash:
            url = f"https://amoy.polygonscan.com/tx/{obj.blockchain_hash}"
            return format_html('<a href="{}" target="_blank">🔗 Ver en PolyScan</a>', url)
        return "—"
    polyscan_link.short_description = 'Transacción'

@admin.register(DeviceEvent)
class DeviceEventAdmin(admin.ModelAdmin):
    list_display = [
        'device_id', 'event_type_display', 'severity_display',
        'resolved_display', 'timestamp', 'created_at'
    ]
    
    list_filter = [
        'event_type', 'severity', 'resolved', 'timestamp'
    ]
    
    search_fields = [
        'device__device_id', 'message', 'resolved_by__username'
    ]
    
    readonly_fields = [
        'created_at', 'device_link', 'resolved_by_link', 'data_prettified'
    ]
    
    fieldsets = (
        ('Información del Evento', {
            'fields': (
                'device_link', 'event_type', 'severity', 'message'
            )
        }),
        ('Datos Adicionales', {
            'fields': ('data_prettified',),
            'classes': ('collapse',)
        }),
        ('Resolución', {
            'fields': (
                'resolved', 'resolved_at', 'resolved_by_link'
            )
        }),
        ('Timestamps', {
            'fields': (
                'timestamp', 'created_at'
            )
        }),
    )
    
    def device_id(self, obj):
        return obj.device.device_id
    device_id.short_description = 'Dispositivo'
    
    def device_link(self, obj):
        if obj.device:
            url = reverse('admin:iot_iotdevice_change', args=[obj.device.id])
            return format_html('<a href="{}">{}</a>', url, obj.device.device_id)
        return "—"
    device_link.short_description = 'Dispositivo'
    
    def event_type_display(self, obj):
        event_colors = {
            'CONNECT': 'green',
            'DISCONNECT': 'red',
            'LOW_BATTERY': 'orange',
            'MAINTENANCE': 'blue',
            'ERROR': 'red',
            'FIRMWARE_UPDATE': 'purple',
            'LOCATION_UPDATE': 'teal',
            'HEALTH_ALERT': 'darkred'
        }
        color = event_colors.get(obj.event_type, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_event_type_display()
        )
    event_type_display.short_description = 'Tipo de Evento'
    
    def severity_display(self, obj):
        severity_colors = {
            'LOW': 'green',
            'MEDIUM': 'orange',
            'HIGH': 'red',
            'CRITICAL': 'darkred'
        }
        color = severity_colors.get(obj.severity, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_severity_display()
        )
    severity_display.short_description = 'Severidad'
    
    def resolved_display(self, obj):
        if obj.resolved:
            return format_html('<span style="color: green;">✅ Resuelto</span>')
        return format_html('<span style="color: red;">❌ Pendiente</span>')
    resolved_display.short_description = 'Resuelto'
    
    def resolved_by_link(self, obj):
        if obj.resolved_by:
            url = reverse('admin:auth_user_change', args=[obj.resolved_by.id])
            return format_html('<a href="{}">{}</a>', url, obj.resolved_by.get_full_name() or obj.resolved_by.username)
        return "—"
    resolved_by_link.short_description = 'Resuelto por'
    
    def data_prettified(self, obj):
        return format_html('<pre style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; overflow-x: auto;">{}</pre>', 
                          json.dumps(obj.data, indent=2, ensure_ascii=False))
    data_prettified.short_description = 'Datos (Formateados)'

@admin.register(DeviceConfiguration)
class DeviceConfigurationAdmin(admin.ModelAdmin):
    list_display = [
        'device_id', 'sampling_interval', 'data_retention',
        'gps_enabled_display', 'health_monitoring_display'
    ]
    
    list_filter = [
        'gps_enabled', 'health_monitoring', 'low_power_mode'
    ]
    
    search_fields = [
        'device__device_id', 'device__name'
    ]
    
    readonly_fields = [
        'created_at', 'updated_at', 'device_link', 'alert_thresholds_prettified'
    ]
    
    fieldsets = (
        ('Dispositivo', {
            'fields': ('device_link',)
        }),
        ('Configuración de Muestreo', {
            'fields': (
                'sampling_interval', 'data_retention'
            )
        }),
        ('Funcionalidades', {
            'fields': (
                'gps_enabled', 'health_monitoring', 'low_power_mode',
                'firmware_auto_update'
            )
        }),
        ('Umbrales de Alerta', {
            'fields': ('alert_thresholds_prettified',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 'updated_at'
            )
        }),
    )
    
    def device_id(self, obj):
        return obj.device.device_id
    device_id.short_description = 'Dispositivo'
    
    def device_link(self, obj):
        if obj.device:
            url = reverse('admin:iot_iotdevice_change', args=[obj.device.id])
            return format_html('<a href="{}">{}</a>', url, obj.device.device_id)
        return "—"
    device_link.short_description = 'Dispositivo'
    
    def gps_enabled_display(self, obj):
        if obj.gps_enabled:
            return format_html('<span style="color: green;">✅ Habilitado</span>')
        return format_html('<span style="color: red;">❌ Deshabilitado</span>')
    gps_enabled_display.short_description = 'GPS'
    
    def health_monitoring_display(self, obj):
        if obj.health_monitoring:
            return format_html('<span style="color: green;">✅ Habilitado</span>')
        return format_html('<span style="color: red;">❌ Deshabilitado</span>')
    health_monitoring_display.short_description = 'Monitoreo Salud'
    
    def alert_thresholds_prettified(self, obj):
        return format_html('<pre style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; overflow-x: auto;">{}</pre>', 
                          json.dumps(obj.alert_thresholds, indent=2, ensure_ascii=False))
    alert_thresholds_prettified.short_description = 'Umbrales (Formateados)'

@admin.register(DeviceAnalytics)
class DeviceAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'device_id', 'date', 'total_readings', 'avg_battery_level_display',
        'connectivity_uptime_display', 'data_quality_score_display',
        'alerts_triggered'
    ]
    
    list_filter = [
        'date', 'device__device_type'
    ]
    
    search_fields = [
        'device__device_id', 'device__name'
    ]
    
    readonly_fields = [
        'created_at', 'device_link', 'data_quality_status'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'device_link', 'date'
            )
        }),
        ('Métricas de Rendimiento', {
            'fields': (
                'total_readings', 'avg_battery_level', 'connectivity_uptime',
                'data_quality_score', 'data_quality_status'
            )
        }),
        ('Alertas y Eventos', {
            'fields': ('alerts_triggered',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def device_id(self, obj):
        return obj.device.device_id
    device_id.short_description = 'Dispositivo'
    
    def device_link(self, obj):
        if obj.device:
            url = reverse('admin:iot_iotdevice_change', args=[obj.device.id])
            return format_html('<a href="{}">{}</a>', url, obj.device.device_id)
        return "—"
    device_link.short_description = 'Dispositivo'
    
    def avg_battery_level_display(self, obj):
        if obj.avg_battery_level:
            color = 'green' if obj.avg_battery_level > 70 else 'orange' if obj.avg_battery_level > 30 else 'red'
            return format_html(
                '<span style="color: {};">{}%</span>',
                color, round(obj.avg_battery_level, 1)
            )
        return "—"
    avg_battery_level_display.short_description = 'Batería Promedio'
    
    def connectivity_uptime_display(self, obj):
        if obj.connectivity_uptime:
            color = 'green' if obj.connectivity_uptime > 95 else 'orange' if obj.connectivity_uptime > 80 else 'red'
            return format_html(
                '<span style="color: {};">{}%</span>',
                color, round(obj.connectivity_uptime, 1)
            )
        return "—"
    connectivity_uptime_display.short_description = 'Disponibilidad'
    
    def data_quality_score_display(self, obj):
        if obj.data_quality_score:
            color = 'green' if obj.data_quality_score > 90 else 'orange' if obj.data_quality_score > 70 else 'red'
            return format_html(
                '<span style="color: {};">{}/100</span>',
                color, round(obj.data_quality_score, 1)
            )
        return "—"
    data_quality_score_display.short_description = 'Calidad Datos'
    
    def data_quality_status(self, obj):
        if obj.data_quality_score:
            if obj.data_quality_score > 90:
                return format_html('<span style="color: green;">✅ Excelente</span>')
            elif obj.data_quality_score > 70:
                return format_html('<span style="color: orange;">⚠️ Aceptable</span>')
            else:
                return format_html('<span style="color: red;">❌ Pobre</span>')
        return "—"
    data_quality_status.short_description = 'Estado Calidad'

# Configuración adicional para el admin de IoT
admin.site.site_header = "🐄 GanadoChain - IoT Administration"