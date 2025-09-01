# blockchain/serializers.py
from rest_framework import serializers
from cattle.models import HealthStatus
import re

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
    metadata = serializers.CharField()

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
    amount = serializers.IntegerField(min_value=1, max_value=1000000)
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
        max_digits=4, 
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
    activity_level = serializers.DecimalField(
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
        max_digits=4, 
        decimal_places=2, 
        required=False, 
        allow_null=True,
        min_value=35.0,
        max_value=42.0
    )
    activity_level = serializers.DecimalField(
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

class ContractInteractionSerializer(serializers.Serializer):
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

class SmartContractSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    contract_type = serializers.ChoiceField(choices=[
        ('NFT', 'Animal NFT'),
        ('TOKEN', 'Ganado Token'),
        ('REGISTRY', 'Registry'),
        ('IOT', 'IoT Manager'),
    ])
    address = EthereumAddressField()
    abi = serializers.JSONField()
    version = serializers.CharField(max_length=20)
    is_active = serializers.BooleanField(default=True)
    deployment_block = serializers.IntegerField(min_value=0)
    deployment_tx_hash = TransactionHashField()

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