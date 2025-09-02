from rest_framework import serializers
from .models import Animal, AnimalHealthRecord, Batch
from django.contrib.auth import get_user_model

User = get_user_model()

class AnimalSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    health_status_display = serializers.CharField(source='get_health_status_display', read_only=True)
    is_minted = serializers.BooleanField(read_only=True)
    metadata_uri = serializers.CharField(read_only=True)
    polyscan_url = serializers.CharField(read_only=True)
    age = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Animal
        fields = [
            'id', 'ear_tag', 'breed', 'birth_date', 'weight', 'health_status', 
            'health_status_display', 'location', 'owner', 'owner_email', 'owner_name',
            'ipfs_hash', 'token_id', 'mint_transaction_hash', 'nft_owner_wallet',
            'is_minted', 'metadata_uri', 'polyscan_url', 'age',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_minted', 'metadata_uri', 'polyscan_url']
    
    def get_age(self, obj):
        from datetime import date
        if obj.birth_date:
            today = date.today()
            return today.year - obj.birth_date.year - ((today.month, today.day) < (obj.birth_date.month, obj.birth_date.day))
        return None
    
    def validate_mint_transaction_hash(self, value):
        import re
        if value and not re.match(r'^(0x)?[0-9a-fA-F]{64}$', value):
            raise serializers.ValidationError('Formato de hash de transacción inválido.')
        return value
    
    def validate_nft_owner_wallet(self, value):
        import re
        if value and not re.match(r'^(0x)?[0-9a-fA-F]{40}$', value):
            raise serializers.ValidationError('Formato de wallet inválido.')
        return value

class AnimalHealthRecordSerializer(serializers.ModelSerializer):
    animal_ear_tag = serializers.CharField(source='animal.ear_tag', read_only=True)
    animal_breed = serializers.CharField(source='animal.breed', read_only=True)
    health_status_display = serializers.CharField(source='get_health_status_display', read_only=True)
    source_display = serializers.CharField(source='get_source_display', read_only=True)
    veterinarian_name = serializers.CharField(source='veterinarian.get_full_name', read_only=True, allow_null=True)
    blockchain_linked = serializers.BooleanField(read_only=True)
    polyscan_url = serializers.CharField(read_only=True)
    
    class Meta:
        model = AnimalHealthRecord
        fields = [
            'id', 'animal', 'animal_ear_tag', 'animal_breed', 'health_status', 
            'health_status_display', 'source', 'source_display', 'veterinarian', 
            'veterinarian_name', 'iot_device_id', 'notes', 'temperature', 
            'heart_rate', 'movement_activity', 'ipfs_hash', 'transaction_hash', 
            'blockchain_hash', 'blockchain_linked', 'polyscan_url', 'created_at'
        ]
        read_only_fields = ['created_at', 'blockchain_linked', 'polyscan_url']
    
    def validate_transaction_hash(self, value):
        import re
        if value and not re.match(r'^(0x)?[0-9a-fA-F]{64}$', value):
            raise serializers.ValidationError('Formato de hash de transacción inválido.')
        return value
    
    def validate_blockchain_hash(self, value):
        import re
        if value and not re.match(r'^(0x)?[0-9a-fA-F]{64}$', value):
            raise serializers.ValidationError('Formato de hash blockchain inválido.')
        return value

class BatchSerializer(serializers.ModelSerializer):
    animals_count = serializers.SerializerMethodField(read_only=True)
    minted_animals_count = serializers.SerializerMethodField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    polyscan_url = serializers.CharField(read_only=True)
    animal_details = AnimalSerializer(many=True, read_only=True, source='animals')
    
    class Meta:
        model = Batch
        fields = [
            'id', 'name', 'animals', 'animal_details', 'origin', 'destination', 
            'status', 'status_display', 'ipfs_hash', 'blockchain_tx', 
            'created_by', 'created_by_name', 'animals_count', 'minted_animals_count',
            'polyscan_url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'animals_count', 'minted_animals_count', 'polyscan_url']
    
    def get_animals_count(self, obj):
        return obj.animals.count()
    
    def get_minted_animals_count(self, obj):
        return obj.animals.filter(token_id__isnull=False).count()
    
    def validate_blockchain_tx(self, value):
        import re
        if value and not re.match(r'^(0x)?[0-9a-fA-F]{64}$', value):
            raise serializers.ValidationError('Formato de hash de transacción inválido.')
        return value

class BatchCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = ['name', 'animals', 'origin', 'destination', 'status', 'created_by']
        ref_name = 'CattleBatchCreateSerializer'  # ← Añadir esta línea
    
    def validate_animals(self, value):
        if value:
            owners = set(animal.owner_id for animal in value)
            if len(owners) > 1:
                raise serializers.ValidationError('Todos los animales deben pertenecer al mismo dueño.')
        return value

class AnimalMintSerializer(serializers.Serializer):
    animal_id = serializers.IntegerField()
    wallet_address = serializers.CharField(max_length=42)
    
    def validate_wallet_address(self, value):
        import re
        if not re.match(r'^(0x)?[0-9a-fA-F]{40}$', value):
            raise serializers.ValidationError('Formato de wallet inválido.')
        return value

class HealthDataSerializer(serializers.Serializer):
    device_id = serializers.CharField(max_length=100)
    animal_ear_tag = serializers.CharField(max_length=100)
    temperature = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    heart_rate = serializers.IntegerField(required=False)
    movement_activity = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    timestamp = serializers.DateTimeField(required=False)
    battery_level = serializers.IntegerField(required=False, min_value=0, max_value=100)
    
    def validate(self, data):
        health_fields = ['temperature', 'heart_rate', 'movement_activity']
        if not any(field in data for field in health_fields):
            raise serializers.ValidationError('Al menos un dato de salud (temperature, heart_rate, movement_activity) debe ser proporcionado.')
        return data