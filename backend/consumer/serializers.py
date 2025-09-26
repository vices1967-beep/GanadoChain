from rest_framework import serializers
from .models import ConsumerTier, ConsumerProfile, QRCodeAccess, ConsumerAccessLog

class ConsumerTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsumerTier
        fields = '__all__'

class ConsumerProfileSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    tier_name = serializers.CharField(source='tier.name', read_only=True)
    
    class Meta:
        model = ConsumerProfile
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class QRCodeAccessSerializer(serializers.ModelSerializer):
    animal_ear_tag = serializers.CharField(source='animal.ear_tag', read_only=True)
    animal_breed = serializers.CharField(source='animal.breed', read_only=True)
    
    class Meta:
        model = QRCodeAccess
        fields = '__all__'

class ConsumerAccessLogSerializer(serializers.ModelSerializer):
    consumer_username = serializers.CharField(source='consumer.username', read_only=True)
    animal_ear_tag = serializers.CharField(source='animal.ear_tag', read_only=True)
    
    class Meta:
        model = ConsumerAccessLog
        fields = '__all__'
        read_only_fields = ['timestamp']