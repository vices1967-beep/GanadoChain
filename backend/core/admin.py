from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import validate_ethereum_address, validate_transaction_hash, validate_ipfs_hash
from .metrics_models import SystemMetrics
import json

@admin.register(SystemMetrics)
class SystemMetricsAdmin(admin.ModelAdmin):
    list_display = [
        'date', 'total_animals', 'total_users', 'total_transactions',
        'active_devices', 'average_gas_price_gwei_display',
        'blockchain_events', 'health_alerts', 'system_uptime_display'
    ]
    
    list_filter = [
        'date'
    ]
    
    search_fields = [
        'date'
    ]
    
    readonly_fields = [
        'date', 'created_at', 'total_animals', 'total_users',
        'total_transactions', 'active_devices', 'average_gas_price',
        'average_gas_price_gwei_display', 'blockchain_events',
        'health_alerts', 'producer_count', 'vet_count',
        'frigorifico_count', 'auditor_count', 'avg_response_time',
        'error_rate_display', 'system_uptime_display',
        'metrics_summary'
    ]
    
    fieldsets = (
        ('Fecha', {
            'fields': ('date',)
        }),
        ('Métricas Principales', {
            'fields': (
                'total_animals', 'total_users', 'total_transactions',
                'active_devices', 'blockchain_events', 'health_alerts'
            )
        }),
        ('Métricas de Usuarios', {
            'fields': (
                'producer_count', 'vet_count', 'frigorifico_count',
                'auditor_count'
            ),
            'classes': ('collapse',)
        }),
        ('Métricas de Rendimiento', {
            'fields': (
                'average_gas_price_gwei_display', 'avg_response_time',
                'error_rate_display', 'system_uptime_display'
            )
        }),
        ('Resumen', {
            'fields': ('metrics_summary',),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def average_gas_price_gwei_display(self, obj):
        if obj.average_gas_price_gwei:
            if obj.average_gas_price_gwei < 30:
                color = 'green'
            elif obj.average_gas_price_gwei < 60:
                color = 'orange'
            else:
                color = 'red'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{} Gwei</span>',
                color, round(obj.average_gas_price_gwei, 2)
            )
        return "—"
    average_gas_price_gwei_display.short_description = 'Precio Gas Promedio'
    
    def error_rate_display(self, obj):
        if obj.error_rate:
            if obj.error_rate < 1:
                color = 'green'
            elif obj.error_rate < 5:
                color = 'orange'
            else:
                color = 'red'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}%</span>',
                color, round(obj.error_rate, 2)
            )
        return "—"
    error_rate_display.short_description = 'Tasa de Error'
    
    def system_uptime_display(self, obj):
        if obj.system_uptime:
            if obj.system_uptime > 99.5:
                color = 'green'
            elif obj.system_uptime > 98:
                color = 'orange'
            else:
                color = 'red'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}%</span>',
                color, round(obj.system_uptime, 2)
            )
        return "—"
    system_uptime_display.short_description = 'Disponibilidad del Sistema'
    
    def metrics_summary(self, obj):
        summary = []
        
        # Resumen de métricas principales
        summary.append(f"📊 Total Animales: {obj.total_animals}")
        summary.append(f"👥 Total Usuarios: {obj.total_users}")
        summary.append(f"🔗 Total Transacciones: {obj.total_transactions}")
        summary.append(f"📱 Dispositivos Activos: {obj.active_devices}")
        
        # Resumen de blockchain
        if obj.blockchain_events > 0:
            summary.append(f"⛓️ Eventos Blockchain: {obj.blockchain_events}")
        
        # Resumen de alertas
        if obj.health_alerts > 0:
            alert_color = "red" if obj.health_alerts > 10 else "orange"
            summary.append(
                f'<span style="color: {alert_color};">⚠️ Alertas de Salud: {obj.health_alerts}</span>'
            )
        
        # Resumen de rendimiento
        if obj.avg_response_time:
            response_color = "green" if obj.avg_response_time < 500 else "orange" if obj.avg_response_time < 1000 else "red"
            summary.append(
                f'<span style="color: {response_color};">⏱️ Tiempo Respuesta: {obj.avg_response_time}ms</span>'
            )
        
        if obj.system_uptime:
            uptime_color = "green" if obj.system_uptime > 99.5 else "orange" if obj.system_uptime > 98 else "red"
            summary.append(
                f'<span style="color: {uptime_color};">🟢 Disponibilidad: {obj.system_uptime}%</span>'
            )
        
        return format_html('<br>'.join(summary))
    metrics_summary.short_description = 'Resumen del Día'

    def has_add_permission(self, request):
        # Las métricas del sistema se generan automáticamente
        return False
    
    def has_delete_permission(self, request, obj=None):
        # No permitir eliminar métricas del sistema
        return False

# Panel de administración para las utilidades/core (si es necesario)
class CoreAdmin(admin.ModelAdmin):
    """Panel de administración para utilidades del core"""
    
    def has_module_permission(self, request):
        # Ocultar el módulo core del admin principal ya que solo tiene utilidades
        return False

# Registro de las utilidades (aunque se oculten del módulo)
admin.site.register([], CoreAdmin)

# Configuración adicional para el admin
admin.site.site_title = "🐄 GanadoChain Administration"
admin.site.index_title = "Dashboard de Administración"
admin.site.site_header = "🐄 GanadoChain - Sistema de Trazabilidad con Blockchain"

# Validadores personalizados para el admin (si se necesitan en forms)
class EthereumAddressValidatorMixin:
    def clean_wallet_address(self):
        value = self.cleaned_data.get('wallet_address')
        if value:
            validate_ethereum_address(value)
        return value

class TransactionHashValidatorMixin:
    def clean_transaction_hash(self):
        value = self.cleaned_data.get('transaction_hash')
        if value:
            validate_transaction_hash(value)
        return value

class IPFSHashValidatorMixin:
    def clean_ipfs_hash(self):
        value = self.cleaned_data.get('ipfs_hash')
        if value:
            validate_ipfs_hash(value)
        return value

# Funciones de utilidad para el admin
def get_admin_change_link(obj, app_label, model_name):
    """Genera un enlace para editar un objeto en el admin"""
    if obj and obj.pk:
        url = reverse(f'admin:{app_label}_{model_name}_change', args=[obj.pk])
        return format_html('<a href="{}">🔗 {}</a>', url, str(obj))
    return "—"

def get_admin_changelist_link(app_label, model_name, query_params=None):
    """Genera un enlace a la lista de objetos en el admin"""
    url = reverse(f'admin:{app_label}_{model_name}_changelist')
    if query_params:
        url += '?' + '&'.join([f'{k}={v}' for k, v in query_params.items()])
    model_verbose_name = f"{app_label}.{model_name}"
    return format_html('<a href="{}">📋 Ver {}</a>', url, model_verbose_name)

def format_json_field(data):
    """Formatea datos JSON para visualización en el admin"""
    if data:
        return format_html(
            '<pre style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; overflow-x: auto; font-size: 12px;">{}</pre>',
            json.dumps(data, indent=2, ensure_ascii=False)
        )
    return "—"

def status_badge(value, good_condition=True):
    """Crea un badge de estado con colores"""
    if good_condition:
        return format_html('<span style="background-color: #28a745; color: white; padding: 2px 6px; border-radius: 10px; font-size: 12px;">✅ {}</span>', value)
    else:
        return format_html('<span style="background-color: #dc3545; color: white; padding: 2px 6px; border-radius: 10px; font-size: 12px;">❌ {}</span>', value)

def warning_badge(value):
    """Crea un badge de advertencia"""
    return format_html('<span style="background-color: #ffc107; color: black; padding: 2px 6px; border-radius: 10px; font-size: 12px;">⚠️ {}</span>', value)

# Registro de filtros personalizados para el admin
class DateRangeFilter(admin.DateFieldListFilter):
    """Filtro personalizado para rangos de fechas"""
    template = 'admin/date_range_filter.html'

class BlockchainStatusFilter(admin.SimpleListFilter):
    """Filtro personalizado para estados blockchain"""
    title = 'Estado Blockchain'
    parameter_name = 'blockchain_status'
    
    def lookups(self, request, model_admin):
        return (
            ('linked', 'En Blockchain'),
            ('not_linked', 'No en Blockchain'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'linked':
            return queryset.exclude(blockchain_hash__isnull=True).exclude(blockchain_hash='')
        if self.value() == 'not_linked':
            return queryset.filter(blockchain_hash__isnull=True) | queryset.filter(blockchain_hash='')