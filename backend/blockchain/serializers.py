from rest_framework import serializers
from cattle.models import HealthStatus
from .models import BlockchainEvent, ContractInteraction, NetworkState, SmartContract, GasPriceHistory, TransactionPool
import re
import json

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
        if value and not re.match(r'^0x[0-9a-f]{64}$', value):
            raise serializers.ValidationError('Hash de transacción inválido')
        return value

class BlockchainEventSerializer(serializers.ModelSerializer):
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    short_hash = serializers.CharField(read_only=True)
    polyscan_url = serializers.CharField(read_only=True)
    animal_ear_tag = serializers.CharField(source='animal.ear_tag', read_only=True, allow_null=True)
    batch_name = serializers.CharField(source='batch.name', read_only=True, allow_null=True)
    metadata_prettified = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = BlockchainEvent
        fields = [
            'id', 'event_type', 'event_type_display', 'transaction_hash', 'short_hash',
            'block_number', 'animal', 'animal_ear_tag', 'batch', 'batch_name',
            'from_address', 'to_address', 'metadata', 'metadata_prettified',
            'polyscan_url', 'created_at'
        ]
        read_only_fields = ['created_at', 'short_hash', 'polyscan_url', 'metadata_prettified']
    
    def get_metadata_prettified(self, obj):
        return json.dumps(obj.metadata, indent=2, ensure_ascii=False)

class ContractInteractionSerializer(serializers.ModelSerializer):
    contract_type_display = serializers.CharField(source='get_contract_type_display', read_only=True)
    action_type_display = serializers.CharField(source='get_action_type_display', read_only=True)
    short_hash = serializers.CharField(read_only=True)
    polyscan_url = serializers.CharField(read_only=True)
    gas_cost_eth = serializers.FloatField(read_only=True)
    gas_cost_usd = serializers.FloatField(read_only=True)
    status_display = serializers.CharField(read_only=True)
    parameters_prettified = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = ContractInteraction
        fields = [
            'id', 'contract_type', 'contract_type_display', 'action_type', 'action_type_display',
            'transaction_hash', 'short_hash', 'block_number', 'caller_address', 'target_address',
            'parameters', 'parameters_prettified', 'gas_used', 'gas_price', 'gas_cost_eth',
            'gas_cost_usd', 'status', 'status_display', 'error_message', 'polyscan_url',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'short_hash', 'polyscan_url', 'gas_cost_eth',
            'gas_cost_usd', 'status_display', 'parameters_prettified'
        ]
    
    def get_parameters_prettified(self, obj):
        return json.dumps(obj.parameters, indent=2, ensure_ascii=False)

class NetworkStateSerializer(serializers.ModelSerializer):
    average_gas_price_gwei = serializers.FloatField(read_only=True)
    sync_status = serializers.CharField(read_only=True)
    last_sync_ago = serializers.CharField(read_only=True)
    network_name_display = serializers.CharField(read_only=True)
    
    class Meta:
        model = NetworkState
        fields = [
            'id', 'last_block_number', 'last_sync_time', 'average_gas_price',
            'average_gas_price_gwei', 'active_nodes', 'chain_id', 'sync_enabled',
            'sync_status', 'last_sync_ago', 'network_name', 'network_name_display',
            'rpc_url', 'block_time', 'native_currency', 'is_testnet', 'created_at'
        ]
        read_only_fields = [
            'created_at', 'average_gas_price_gwei', 'sync_status', 'last_sync_ago',
            'network_name_display'
        ]

class SmartContractSerializer(serializers.ModelSerializer):
    contract_type_display = serializers.CharField(source='get_contract_type_display', read_only=True)
    short_address = serializers.CharField(read_only=True)
    polyscan_url = serializers.CharField(read_only=True)
    deployment_polyscan_url = serializers.CharField(read_only=True)
    abi_prettified = serializers.SerializerMethodField(read_only=True)
    is_upgradeable_display = serializers.CharField(read_only=True)
    is_active_display = serializers.CharField(read_only=True)
    
    class Meta:
        model = SmartContract
        fields = [
            'id', 'name', 'contract_type', 'contract_type_display', 'address', 'short_address',
            'abi', 'abi_prettified', 'version', 'is_active', 'is_active_display',
            'deployment_block', 'deployment_tx_hash', 'deployer_address',
            'implementation_address', 'proxy_address', 'is_upgradeable', 'is_upgradeable_display',
            'admin_address', 'polyscan_url', 'deployment_polyscan_url', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'short_address', 'polyscan_url',
            'deployment_polyscan_url', 'abi_prettified', 'is_upgradeable_display',
            'is_active_display'
        ]
    
    def get_abi_prettified(self, obj):
        return json.dumps(obj.abi, indent=2, ensure_ascii=False)

class GasPriceHistorySerializer(serializers.ModelSerializer):
    gas_price_gwei = serializers.FloatField(read_only=True)
    
    class Meta:
        model = GasPriceHistory
        fields = [
            'id', 'gas_price', 'gas_price_gwei', 'block_number', 'timestamp'
        ]
        read_only_fields = ['timestamp']

class TransactionPoolSerializer(serializers.ModelSerializer):
    short_hash = serializers.CharField(read_only=True)
    polyscan_url = serializers.CharField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = TransactionPool
        fields = [
            'id', 'transaction_hash', 'short_hash', 'raw_transaction', 'status',
            'status_display', 'retry_count', 'last_retry', 'polyscan_url',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'short_hash', 'polyscan_url', 'status_display'
        ]

class AssignRoleSerializer(serializers.Serializer):
    target_wallet = EthereumAddressField()
    role = serializers.CharField(max_length=50)

    def validate_role(self, value):
        roles_validos = ['PRODUCER_ROLE', 'VET_ROLE', 'FRIGORIFICO_ROLE', 
                        'AUDITOR_ROLE', 'IOT_ROLE', 'DAO_ROLE']
        if value not in roles_validos:
            raise serializers.ValidationError(f'Rol inválido. Roles válidos: {", ".join(roles_validos)}')
        return value

class MintNFTSerializer(serializers.Serializer):
    animal_id = serializers.IntegerField(min_value=1)
    owner_wallet = EthereumAddressField()
    metadata_uri = serializers.CharField(max_length=255)
    operational_ipfs = serializers.CharField(required=False, allow_blank=True, max_length=255)

    def validate_metadata_uri(self, value):
        if not value.startswith(('ipfs://', 'https://', 'http://')):
            raise serializers.ValidationError('Metadata URI debe comenzar con ipfs://, https:// o http://')
        return value

class RegisterAnimalSerializer(serializers.Serializer):
    animal_id = serializers.IntegerField(min_value=1)
    metadata = serializers.JSONField()

class CheckRoleSerializer(serializers.Serializer):
    wallet_address = EthereumAddressField()
    role_name = serializers.CharField(max_length=50)

    def validate_role_name(self, value):
        roles_validos = ['PRODUCER_ROLE', 'VET_ROLE', 'FRIGORIFICO_ROLE', 
                        'AUDITOR_ROLE', 'IOT_ROLE', 'DAO_ROLE']
        if value not in roles_validos:
            raise serializers.ValidationError(f'Rol inválido. Roles válidos: {", ".join(roles_validos)}')
        return value

class MintTokensSerializer(serializers.Serializer):
    to_wallet = EthereumAddressField()
    amount = serializers.DecimalField(max_digits=18, decimal_places=0, min_value=1, max_value=1000000000000000000)
    batch_id = serializers.CharField(required=False, allow_blank=True, max_length=100)

class UpdateHealthSerializer(serializers.Serializer):
    animal_id = serializers.IntegerField(min_value=1)
    health_status = serializers.ChoiceField(choices=HealthStatus.choices)
    source = serializers.ChoiceField(choices=[
        ('VETERINARIAN', 'Veterinario'),
        ('IOT_SENSOR', 'Sensor IoT'),
        ('FARMER', 'Granjero'),
        ('SYSTEM', 'Sistema Automático')
    ], default='VETERINARIAN')
    veterinarian_wallet = EthereumAddressField(required=False, allow_blank=True)
    iot_device_id = serializers.CharField(max_length=100, required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True, max_length=500)
    temperature = serializers.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        required=False, 
        allow_null=True,
        min_value=35.0,
        max_value=42.0
    )
    heart_rate = serializers.IntegerField(
        required=False, 
        allow_null=True,
        min_value=30,
        max_value=200
    )
    movement_activity = serializers.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        required=False, 
        allow_null=True,
        min_value=0,
        max_value=100
    )

    def validate(self, data):
        # Validar que si la fuente es VETERINARIAN, se proporcione veterinarian_wallet
        if data.get('source') == 'VETERINARIAN' and not data.get('veterinarian_wallet'):
            raise serializers.ValidationError({
                'veterinarian_wallet': 'Se requiere wallet de veterinario para esta fuente'
            })
        
        # Validar que si la fuente es IOT_SENSOR, se proporcione iot_device_id
        if data.get('source') == 'IOT_SENSOR' and not data.get('iot_device_id'):
            raise serializers.ValidationError({
                'iot_device_id': 'Se requiere ID de dispositivo IoT para esta fuente'
            })
        
        return data

class IoTHealthDataSerializer(serializers.Serializer):
    device_id = serializers.CharField(max_length=100)
    animal_ear_tag = serializers.CharField(max_length=100)
    heart_rate = serializers.IntegerField(
        required=False, 
        allow_null=True,
        min_value=30,
        max_value=200
    )
    temperature = serializers.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        required=False, 
        allow_null=True,
        min_value=35.0,
        max_value=42.0
    )
    movement_activity = serializers.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        required=False, 
        allow_null=True,
        min_value=0,
        max_value=100
    )
    rumination_time = serializers.IntegerField(
        required=False, 
        allow_null=True,
        min_value=0,
        max_value=1440
    )
    feeding_activity = serializers.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        required=False, 
        allow_null=True,
        min_value=0,
        max_value=100
    )
    timestamp = serializers.DateTimeField()
    location_lat = serializers.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        required=False, 
        allow_null=True,
        min_value=-90,
        max_value=90
    )
    location_lng = serializers.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        required=False, 
        allow_null=True,
        min_value=-180,
        max_value=180
    )

class AnimalHistorySerializer(serializers.Serializer):
    transaction_hash = TransactionHashField()
    block_number = serializers.IntegerField(min_value=0)
    type = serializers.CharField()
    from_address = EthereumAddressField()
    to_address = EthereumAddressField()
    timestamp = serializers.IntegerField(min_value=0)
    gas_used = serializers.IntegerField(required=False, allow_null=True)
    gas_price = serializers.IntegerField(required=False, allow_null=True)

class BatchCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    animal_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        min_length=1,
        max_length=100
    )
    origin = serializers.CharField(max_length=255)
    destination = serializers.CharField(max_length=255)
    metadata_uri = serializers.CharField(required=False, allow_blank=True, max_length=255)
    notes = serializers.CharField(required=False, allow_blank=True, max_length=500)

class ContractCallSerializer(serializers.Serializer):
    contract_address = EthereumAddressField()
    function_name = serializers.CharField(max_length=100)
    parameters = serializers.JSONField(default=dict)
    value = serializers.IntegerField(default=0, min_value=0)
    gas_limit = serializers.IntegerField(required=False, allow_null=True, min_value=21000, max_value=1000000)

class NetworkStatusSerializer(serializers.Serializer):
    chain_id = serializers.IntegerField()
    block_number = serializers.IntegerField(min_value=0)
    gas_price = serializers.IntegerField(min_value=0)
    is_syncing = serializers.BooleanField()
    peer_count = serializers.IntegerField(min_value=0)
    last_update = serializers.DateTimeField()

class TransactionStatusSerializer(serializers.Serializer):
    transaction_hash = TransactionHashField()
    status = serializers.ChoiceField(choices=[
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('FAILED', 'Failed')
    ])
    block_number = serializers.IntegerField(required=False, allow_null=True)
    gas_used = serializers.IntegerField(required=False, allow_null=True)
    confirmations = serializers.IntegerField(required=False, allow_null=True)

class GasPriceSerializer(serializers.Serializer):
    standard = serializers.IntegerField(min_value=0)
    fast = serializers.IntegerField(min_value=0)
    instant = serializers.IntegerField(min_value=0)
    base_fee = serializers.IntegerField(min_value=0)

class EventSubscriptionSerializer(serializers.Serializer):
    event_name = serializers.CharField(max_length=100)
    contract_address = EthereumAddressField()
    from_block = serializers.IntegerField(min_value=0, required=False)
    to_block = serializers.IntegerField(min_value=0, required=False)
    filters = serializers.JSONField(required=False, default=dict)

class WebhookSerializer(serializers.Serializer):
    url = serializers.URLField()
    event_type = serializers.ChoiceField(choices=[
        ('NFT_MINTED', 'NFT Minted'),
        ('TOKEN_TRANSFER', 'Token Transfer'),
        ('HEALTH_UPDATE', 'Health Update'),
        ('BATCH_CREATED', 'Batch Created'),
        ('CONTRACT_EVENT', 'Contract Event'),
    ])
    is_active = serializers.BooleanField(default=True)
    secret_token = serializers.CharField(required=False, allow_blank=True, max_length=100)

class BlockchainStatsSerializer(serializers.Serializer):
    total_events = serializers.IntegerField(min_value=0)
    total_transactions = serializers.IntegerField(min_value=0)
    successful_transactions = serializers.IntegerField(min_value=0)
    failed_transactions = serializers.IntegerField(min_value=0)
    average_gas_price = serializers.IntegerField(min_value=0)
    total_gas_used = serializers.IntegerField(min_value=0)
    last_block_number = serializers.IntegerField(min_value=0)
    active_contracts = serializers.IntegerField(min_value=0)
    pending_transactions = serializers.IntegerField(min_value=0)