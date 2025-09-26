from rest_framework import serializers
from .models import ConsumerAnalytics, CarbonFootprint

class ConsumerAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsumerAnalytics
        fields = '__all__'
        read_only_fields = ['date']

class CarbonFootprintSerializer(serializers.ModelSerializer):
    animal_ear_tag = serializers.CharField(source='animal.ear_tag', read_only=True)
    certification_name = serializers.CharField(source='certification.name', read_only=True)
    
    class Meta:
        model = CarbonFootprint
        fields = '__all__'