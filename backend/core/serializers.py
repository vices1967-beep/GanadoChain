from rest_framework import serializers
from decimal import Decimal
from .models import SystemMetrics

class EthereumAddressField(serializers.CharField):
    """Campo personalizado para validar direcciones Ethereum"""
    def __init__(self, **kwargs):
        kwargs['max_length'] = 42
        super().__init__(**kwargs)
    
    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        # Normalizar a minúsculas y asegurar prefijo 0x
        if data and not data.startswith('0x'):
            data = '0x' + data
        return data.lower()
    
    def validate(self, value):
        import re
        if value and not re.match(r'^0x[0-9a-f]{40}$', value):
            raise serializers.ValidationError('Dirección Ethereum inválida')
        return value

class TransactionHashField(serializers.CharField):
    """Campo personalizado para validar hashes de transacción"""
    def __init__(self, **kwargs):
        kwargs['max_length'] = 66
        super().__init__(**kwargs)
    
    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        # Asegurar prefijo 0x
        if data and not data.startswith('0x'):
            data = '0x' + data
        return data.lower()
    
    def validate(self, value):
        import re
        if value and not re.match(r'^0x[0-9a-f]{64}$', value):
            raise serializers.ValidationError('Hash de transacción inválido')
        return value

class IPFSHashField(serializers.CharField):
    """Campo personalizado para validar hashes IPFS"""
    def __init__(self, **kwargs):
        kwargs['max_length'] = 46
        super().__init__(**kwargs)
    
    def validate(self, value):
        import re
        if value and not re.match(r'^[Qm][1-9A-Za-z]{44}$', value):
            raise serializers.ValidationError('Hash IPFS inválido')
        return value

class SystemMetricsSerializer(serializers.ModelSerializer):
    """Serializer para métricas del sistema"""
    
    class Meta:
        model = SystemMetrics
        fields = [
            'id', 'date', 'total_animals', 'total_users', 'total_transactions',
            'active_devices', 'average_gas_price', 'blockchain_events',
            'health_alerts', 'producer_count', 'vet_count', 'frigorifico_count',
            'auditor_count', 'avg_response_time', 'error_rate', 'system_uptime',
            'created_at'
        ]
        read_only_fields = ['created_at']

class SystemMetricsSummarySerializer(serializers.Serializer):
    """Serializer para resumen de métricas del sistema"""
    date_range = serializers.CharField(read_only=True)
    total_animals = serializers.IntegerField(min_value=0)
    total_users = serializers.IntegerField(min_value=0)
    total_transactions = serializers.IntegerField(min_value=0)
    active_devices = serializers.IntegerField(min_value=0)
    avg_gas_price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0'))
    blockchain_events = serializers.IntegerField(min_value=0)
    health_alerts = serializers.IntegerField(min_value=0)
    
    # Métricas por tipo de usuario
    producer_count = serializers.IntegerField(min_value=0)
    vet_count = serializers.IntegerField(min_value=0)
    frigorifico_count = serializers.IntegerField(min_value=0)
    auditor_count = serializers.IntegerField(min_value=0)
    
    # Métricas de rendimiento
    avg_response_time = serializers.DecimalField(max_digits=6, decimal_places=2, min_value=Decimal('0'))
    error_rate = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=Decimal('0'), max_value=Decimal('100'))
    system_uptime = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=Decimal('0'), max_value=Decimal('100'))

class HealthCheckSerializer(serializers.Serializer):
    """Serializer para health check del sistema"""
    status = serializers.CharField()
    timestamp = serializers.DateTimeField()
    database = serializers.BooleanField()
    blockchain = serializers.BooleanField()
    iot_devices = serializers.BooleanField()
    version = serializers.CharField()
    uptime = serializers.DurationField()
    memory_usage = serializers.DecimalField(max_digits=8, decimal_places=2, min_value=Decimal('0'))
    cpu_usage = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=Decimal('0'), max_value=Decimal('100'))

class SystemConfigSerializer(serializers.Serializer):
    """Serializer para configuración del sistema"""
    blockchain_rpc_url = serializers.URLField()
    blockchain_chain_id = serializers.IntegerField(min_value=1)
    ipfs_gateway_url = serializers.URLField()
    max_gas_price = serializers.IntegerField(min_value=0)
    min_gas_price = serializers.IntegerField(min_value=0)
    default_gas_limit = serializers.IntegerField(min_value=21000)
    transaction_timeout = serializers.IntegerField(min_value=30)
    sync_interval = serializers.IntegerField(min_value=10)
    health_check_interval = serializers.IntegerField(min_value=5)
    max_retries = serializers.IntegerField(min_value=1, max_value=10)

class DashboardStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas del dashboard"""
    total_animals = serializers.IntegerField(min_value=0)
    total_batches = serializers.IntegerField(min_value=0)
    total_devices = serializers.IntegerField(min_value=0)
    total_users = serializers.IntegerField(min_value=0)
    
    healthy_animals = serializers.IntegerField(min_value=0)
    sick_animals = serializers.IntegerField(min_value=0)
    under_observation = serializers.IntegerField(min_value=0)
    
    active_batches = serializers.IntegerField(min_value=0)
    delivered_batches = serializers.IntegerField(min_value=0)
    in_transit_batches = serializers.IntegerField(min_value=0)
    
    online_devices = serializers.IntegerField(min_value=0)
    offline_devices = serializers.IntegerField(min_value=0)
    low_battery_devices = serializers.IntegerField(min_value=0)
    
    pending_transactions = serializers.IntegerField(min_value=0)
    confirmed_transactions = serializers.IntegerField(min_value=0)
    failed_transactions = serializers.IntegerField(min_value=0)
    
    current_gas_price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0'))
    avg_block_time = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=Decimal('0'))
    network_status = serializers.CharField()

class ValidationTestSerializer(serializers.Serializer):
    """Serializer para probar validaciones"""
    ethereum_address = EthereumAddressField(required=False)
    transaction_hash = TransactionHashField(required=False)
    ipfs_hash = IPFSHashField(required=False)
    decimal_value = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False,
        min_value=Decimal('0.01'),
        max_value=Decimal('1000.00')
    )
    integer_value = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=1000
    )

class ErrorResponseSerializer(serializers.Serializer):
    """Serializer para respuestas de error estandarizadas"""
    error = serializers.CharField()
    code = serializers.IntegerField()
    message = serializers.CharField()
    details = serializers.JSONField(required=False)
    timestamp = serializers.DateTimeField()

class SuccessResponseSerializer(serializers.Serializer):
    """Serializer para respuestas exitosas estandarizadas"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = serializers.JSONField(required=False)
    timestamp = serializers.DateTimeField()

class PaginationSerializer(serializers.Serializer):
    """Serializer para información de paginación"""
    count = serializers.IntegerField(min_value=0)
    next = serializers.URLField(required=False, allow_null=True)
    previous = serializers.URLField(required=False, allow_null=True)
    page = serializers.IntegerField(min_value=1)
    page_size = serializers.IntegerField(min_value=1)
    total_pages = serializers.IntegerField(min_value=1)