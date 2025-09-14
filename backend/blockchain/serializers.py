from rest_framework import serializers
from cattle.models import HealthStatus
from .models import BlockchainEvent, ContractInteraction, NetworkState, SmartContract, GasPriceHistory, TransactionPool, GovernanceProposal, Vote
from .market_models import MarketListing, Trade
from cattle.blockchain_models import CertificationStandard, AnimalCertification
import re
import json
from decimal import Decimal
from django.core.exceptions import ValidationError
from web3 import Web3

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
    target_wallet = serializers.CharField(max_length=42)
    role = serializers.CharField(max_length=50)
    
    def validate_target_wallet(self, value):
        w3 = Web3()
        if not w3.is_address(value):
            raise serializers.ValidationError("Dirección de wallet inválida")
        return value

# ... (otros serializers)

class MintNFTSerializer(serializers.Serializer):
    animal_id = serializers.IntegerField()
    owner_wallet = serializers.CharField(max_length=42)
    metadata_uri = serializers.CharField(required=True)
    operational_ipfs = serializers.CharField(required=False, allow_blank=True)
    
    def validate_owner_wallet(self, value):
        # Normalizar la dirección
        if value and not value.startswith('0x'):
            value = '0x' + value
        
        w3 = Web3()
        if not w3.is_address(value):
            raise serializers.ValidationError("Dirección de wallet inválida")
        
        # Asegurar que tenga exactamente 42 caracteres
        if len(value) != 42:
            raise serializers.ValidationError("La dirección debe tener exactamente 42 caracteres")
        
        return value
    
    def validate_metadata_uri(self, value):
        if not value:
            raise serializers.ValidationError("metadata_uri es requerido")
        if not value.startswith('ipfs://'):
            raise serializers.ValidationError("metadata_uri debe comenzar con 'ipfs://'")
        return value
    
    def validate(self, data):
        # Validación adicional cruzada si es necesaria
        return data

    # ... el resto del serializer ...
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
    to_wallet = serializers.CharField(max_length=42)
    amount = serializers.CharField()
    
    def validate_to_wallet(self, value):
        w3 = Web3()
        if not w3.is_address(value):
            raise serializers.ValidationError("Dirección de wallet inválida")
        return value
    
    def validate_amount(self, value):
        try:
            # Validar que el amount sea un número válido
            amount = int(value)
            if amount <= 0:
                raise serializers.ValidationError("El amount debe ser mayor a 0")
            return value
        except ValueError:
            raise serializers.ValidationError("Amount debe ser un número válido")

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
        min_value=Decimal('35.0'),
        max_value=Decimal('42.0')
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
        min_value=Decimal('0'),
        max_value=Decimal('100')
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
        min_value=Decimal('35.0'),
        max_value=Decimal('42.0')
    )
    movement_activity = serializers.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        required=False, 
        allow_null=True,
        min_value=Decimal('0'),
        max_value=Decimal('100')
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
        min_value=Decimal('0'),
        max_value=Decimal('100')
    )
    timestamp = serializers.DateTimeField()
    location_lat = serializers.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        required=False, 
        allow_null=True,
        min_value=Decimal('-90'),
        max_value=Decimal('90')
    )
    location_lng = serializers.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        required=False, 
        allow_null=True,
        min_value=Decimal('-180'),
        max_value=Decimal('180')
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

    class Meta:
        ref_name = 'BlockchainBatchCreateSerializer'

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

# Añadir al archivo de serializers existente

# Serializers para Certificaciones y Cumplimiento Normativo
class CertificationStandardSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificationStandard
        fields = [
            'id', 'name', 'description', 'issuing_authority', 'validity_days',
            'requirements', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class AnimalCertificationSerializer(serializers.ModelSerializer):
    animal_ear_tag = serializers.CharField(source='animal.ear_tag', read_only=True)
    animal_breed = serializers.CharField(source='animal.breed', read_only=True)
    standard_name = serializers.CharField(source='standard.name', read_only=True)
    certifying_authority_name = serializers.CharField(source='certifying_authority.get_full_name', read_only=True)
    certifying_authority_email = serializers.EmailField(source='certifying_authority.email', read_only=True)
    blockchain_linked = serializers.SerializerMethodField(read_only=True)
    polyscan_url = serializers.SerializerMethodField(read_only=True)
    is_expired = serializers.SerializerMethodField(read_only=True)
    is_valid = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = AnimalCertification
        fields = [
            'id', 'animal', 'animal_ear_tag', 'animal_breed', 'standard', 'standard_name',
            'certification_date', 'expiration_date', 'certifying_authority',
            'certifying_authority_name', 'certifying_authority_email', 'evidence',
            'blockchain_hash', 'revoked', 'revocation_reason', 'blockchain_linked',
            'polyscan_url', 'is_expired', 'is_valid', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'blockchain_linked', 'polyscan_url', 'is_expired', 'is_valid']
    
    def get_blockchain_linked(self, obj):
        return bool(obj.blockchain_hash)
    
    def get_polyscan_url(self, obj):
        if obj.blockchain_hash:
            return f"https://polygonscan.com/tx/{obj.blockchain_hash}"
        return None
    
    def get_is_expired(self, obj):
        from django.utils import timezone
        return obj.expiration_date < timezone.now() if obj.expiration_date else False
    
    def get_is_valid(self, obj):
        from django.utils import timezone
        return not obj.revoked and (obj.expiration_date > timezone.now() if obj.expiration_date else True)
    
    def validate_blockchain_hash(self, value):
        import re
        if value and not re.match(r'^(0x)?[0-9a-fA-F]{64}$', value):
            raise serializers.ValidationError('Formato de hash blockchain inválido.')
        return value
    
    def validate_certifying_authority(self, value):
        if value.role != 'auditor':
            raise serializers.ValidationError('El usuario debe tener el rol de auditor.')
        return value

class AnimalCertificationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimalCertification
        fields = ['animal', 'standard', 'certification_date', 'expiration_date', 'certifying_authority', 'evidence']

class CertificationEvidenceSerializer(serializers.Serializer):
    document_url = serializers.URLField()
    inspection_date = serializers.DateField()
    inspector_name = serializers.CharField(max_length=200)
    compliance_score = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0, max_value=100)
    notes = serializers.CharField(required=False, allow_blank=True, max_length=500)

# Serializers para Sistema de Gobernanza Mejorado
class GovernanceProposalSerializer(serializers.ModelSerializer):
    proposed_by_name = serializers.CharField(source='proposed_by.get_full_name', read_only=True)
    proposed_by_email = serializers.EmailField(source='proposed_by.email', read_only=True)
    proposal_type_display = serializers.CharField(source='get_proposal_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    voting_status = serializers.SerializerMethodField(read_only=True)
    total_votes = serializers.SerializerMethodField(read_only=True)
    yes_votes = serializers.SerializerMethodField(read_only=True)
    no_votes = serializers.SerializerMethodField(read_only=True)
    parameters_prettified = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = GovernanceProposal
        fields = [
            'id', 'title', 'description', 'proposal_type', 'proposal_type_display',
            'proposed_by', 'proposed_by_name', 'proposed_by_email', 'created_at',
            'voting_start', 'voting_end', 'parameters', 'parameters_prettified',
            'status', 'status_display', 'blockchain_proposal_id', 'voting_status',
            'total_votes', 'yes_votes', 'no_votes'
        ]
        read_only_fields = ['created_at', 'voting_status', 'total_votes', 'yes_votes', 'no_votes', 'parameters_prettified']
    
    def get_voting_status(self, obj):
        from django.utils import timezone
        now = timezone.now()
        if now < obj.voting_start:
            return 'PENDING'
        elif obj.voting_start <= now <= obj.voting_end:
            return 'ACTIVE'
        else:
            return 'COMPLETED'
    
    def get_total_votes(self, obj):
        return obj.votes.count()
    
    def get_yes_votes(self, obj):
        return obj.votes.filter(vote_value=True).count()
    
    def get_no_votes(self, obj):
        return obj.votes.filter(vote_value=False).count()
    
    def get_parameters_prettified(self, obj):
        return json.dumps(obj.parameters, indent=2, ensure_ascii=False) if obj.parameters else None

class VoteSerializer(serializers.ModelSerializer):
    voter_name = serializers.CharField(source='voter.get_full_name', read_only=True)
    voter_email = serializers.EmailField(source='voter.email', read_only=True)
    proposal_title = serializers.CharField(source='proposal.title', read_only=True)
    vote_value_display = serializers.CharField(source='get_vote_value_display', read_only=True)
    polyscan_url = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Vote
        fields = [
            'id', 'proposal', 'proposal_title', 'voter', 'voter_name', 'voter_email',
            'vote_value', 'vote_value_display', 'voting_power', 'blockchain_vote_hash',
            'polyscan_url', 'created_at'
        ]
        read_only_fields = ['created_at', 'polyscan_url']
    
    def get_polyscan_url(self, obj):
        if obj.blockchain_vote_hash:
            return f"https://polygonscan.com/tx/{obj.blockchain_vote_hash}"
        return None
    
    def validate_blockchain_vote_hash(self, value):
        import re
        if value and not re.match(r'^(0x)?[0-9a-fA-F]{64}$', value):
            raise serializers.ValidationError('Formato de hash blockchain inválido.')
        return value

class CreateVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['proposal', 'vote_value']

class ProposalParameterSerializer(serializers.Serializer):
    parameter_name = serializers.CharField(max_length=100)
    current_value = serializers.CharField()
    proposed_value = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True, max_length=500)

# Serializers para Comercio y Mercado
class MarketListingSerializer(serializers.ModelSerializer):
    animal_ear_tag = serializers.CharField(source='animal.ear_tag', read_only=True)
    animal_breed = serializers.CharField(source='animal.breed', read_only=True)
    animal_health_status = serializers.CharField(source='animal.health_status', read_only=True)
    seller_name = serializers.CharField(source='seller.get_full_name', read_only=True)
    seller_email = serializers.EmailField(source='seller.email', read_only=True)
    is_expired = serializers.SerializerMethodField(read_only=True)
    days_until_expiration = serializers.SerializerMethodField(read_only=True)
    polyscan_url = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = MarketListing
        fields = [
            'id', 'animal', 'animal_ear_tag', 'animal_breed', 'animal_health_status',
            'seller', 'seller_name', 'seller_email', 'price', 'currency',
            'listing_date', 'expiration_date', 'is_active', 'blockchain_listing_id',
            'is_expired', 'days_until_expiration', 'polyscan_url'
        ]
        read_only_fields = ['listing_date', 'is_expired', 'days_until_expiration', 'polyscan_url']
    
    def get_is_expired(self, obj):
        from django.utils import timezone
        return obj.expiration_date < timezone.now() if obj.expiration_date else False
    
    def get_days_until_expiration(self, obj):
        from django.utils import timezone
        if obj.expiration_date:
            delta = obj.expiration_date - timezone.now()
            return max(0, delta.days)
        return None
    
    def get_polyscan_url(self, obj):
        if obj.blockchain_listing_id:
            # Asumiendo que el listing ID se puede usar para construir una URL
            return f"https://polygonscan.com/address/{obj.blockchain_listing_id}"
        return None

class TradeSerializer(serializers.ModelSerializer):
    animal_ear_tag = serializers.CharField(source='listing.animal.ear_tag', read_only=True)
    seller_name = serializers.CharField(source='listing.seller.get_full_name', read_only=True)
    buyer_name = serializers.CharField(source='buyer.get_full_name', read_only=True)
    polyscan_url = serializers.SerializerMethodField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Trade
        fields = [
            'id', 'listing', 'animal_ear_tag', 'buyer', 'buyer_name', 'seller_name',
            'transaction_hash', 'trade_date', 'price', 'platform_fee',
            'status', 'status_display', 'polyscan_url'
        ]
        read_only_fields = ['trade_date', 'polyscan_url', 'status_display']
    
    def get_polyscan_url(self, obj):
        if obj.transaction_hash:
            return f"https://polygonscan.com/tx/{obj.transaction_hash}"
        return None
    
    def validate_transaction_hash(self, value):
        import re
        if value and not re.match(r'^(0x)?[0-9a-fA-F]{64}$', value):
            raise serializers.ValidationError('Formato de hash de transacción inválido.')
        return value

class CreateMarketListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketListing
        fields = ['animal', 'price', 'currency', 'expiration_date']

class ExecuteTradeSerializer(serializers.Serializer):
    listing_id = serializers.IntegerField(min_value=1)
    buyer_wallet = serializers.CharField(max_length=42)
    
    def validate_buyer_wallet(self, value):
        import re
        if not re.match(r'^(0x)?[0-9a-fA-F]{40}$', value):
            raise serializers.ValidationError('Formato de wallet inválido.')
        return value

class MarketStatsSerializer(serializers.Serializer):
    total_listings = serializers.IntegerField(min_value=0)
    active_listings = serializers.IntegerField(min_value=0)
    total_trades = serializers.IntegerField(min_value=0)
    total_volume = serializers.DecimalField(max_digits=20, decimal_places=2)
    average_price = serializers.DecimalField(max_digits=20, decimal_places=2)
    platform_fees = serializers.DecimalField(max_digits=20, decimal_places=2)

class PriceHistorySerializer(serializers.Serializer):
    animal_id = serializers.IntegerField(min_value=1)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    
    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError('La fecha de inicio no puede ser posterior a la fecha de fin.')
        return data
    
# Agregar al final de blockchain/serializers.py

class CreateProposalSerializer(serializers.ModelSerializer):
    """Serializer para crear nuevas propuestas de gobernanza"""
    class Meta:
        model = GovernanceProposal
        fields = ['title', 'description', 'proposal_type', 'voting_start', 'voting_end', 'parameters']
    
    def validate_voting_start(self, value):
        from django.utils import timezone
        if value <= timezone.now():
            raise serializers.ValidationError('La fecha de inicio de votación debe ser en el futuro.')
        return value
    
    def validate_voting_end(self, value):
        from django.utils import timezone
        voting_start = self.initial_data.get('voting_start')
        
        if voting_start:
            try:
                voting_start = timezone.datetime.fromisoformat(voting_start.replace('Z', '+00:00'))
                if value <= voting_start:
                    raise serializers.ValidationError('La fecha de fin de votación debe ser posterior a la fecha de inicio.')
            except (ValueError, TypeError):
                pass
        
        if value <= timezone.now():
            raise serializers.ValidationError('La fecha de fin de votación debe ser en el futuro.')
        
        return value
    
    def validate_parameters(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError('Los parámetros deben ser un objeto JSON.')
        return value

# Agregar al final de blockchain/serializers.py

class PublicCertificationSerializer(serializers.ModelSerializer):
    """Serializer público para certificaciones (sin información sensible)"""
    animal_ear_tag = serializers.CharField(source='animal.ear_tag', read_only=True)
    animal_breed = serializers.CharField(source='animal.breed', read_only=True)
    standard_name = serializers.CharField(source='standard.name', read_only=True)
    is_expired = serializers.SerializerMethodField(read_only=True)
    is_valid = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = AnimalCertification
        fields = [
            'id', 'animal_ear_tag', 'animal_breed', 'standard_name',
            'certification_date', 'expiration_date', 'is_expired', 'is_valid'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_is_expired(self, obj):
        from django.utils import timezone
        return obj.expiration_date < timezone.now() if obj.expiration_date else False
    
    def get_is_valid(self, obj):
        from django.utils import timezone
        return not obj.revoked and (obj.expiration_date > timezone.now() if obj.expiration_date else True)
    
    def to_representation(self, instance):
        """Ocultar información sensible para el público"""
        data = super().to_representation(instance)
        # Remover campos sensibles si están presentes
        sensitive_fields = [
            'certifying_authority', 'evidence', 'blockchain_hash',
            'revoked', 'revocation_reason', 'standard'
        ]
        for field in sensitive_fields:
            if field in data:
                del data[field]
        return data
    
# Agregar al final de blockchain/serializers.py

class PublicBlockchainEventSerializer(serializers.ModelSerializer):
    """Serializer público para eventos blockchain (sin información sensible)"""
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    short_hash = serializers.CharField(read_only=True)
    polyscan_url = serializers.CharField(read_only=True)
    animal_ear_tag = serializers.CharField(source='animal.ear_tag', read_only=True, allow_null=True)
    batch_name = serializers.CharField(source='batch.name', read_only=True, allow_null=True)
    
    class Meta:
        model = BlockchainEvent
        fields = [
            'id', 'event_type', 'event_type_display', 'short_hash',
            'block_number', 'animal_ear_tag', 'batch_name', 'polyscan_url',
            'created_at'
        ]
        read_only_fields = ['created_at', 'short_hash', 'polyscan_url']
    
    def to_representation(self, instance):
        """Ocultar información sensible para el público"""
        data = super().to_representation(instance)
        # Remover campos sensibles
        sensitive_fields = [
            'transaction_hash', 'from_address', 'to_address', 'metadata',
            'animal', 'batch'
        ]
        for field in sensitive_fields:
            if field in data:
                del data[field]
        return data