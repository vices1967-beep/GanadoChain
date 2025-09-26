from rest_framework import serializers
from .models import GlobalCertificationBody, Certification, CertificationStandard

class GlobalCertificationBodySerializer(serializers.ModelSerializer):
    """Serializer para organismos de certificación"""
    active_certifications = serializers.SerializerMethodField()
    supported_standards = serializers.SerializerMethodField()
    
    class Meta:
        model = GlobalCertificationBody
        fields = [
            'id', 'name', 'accreditation_number', 'country',
            'certification_type', 'international_scope', 
            'recognized_standards', 'active_certifications',
            'supported_standards', 'website'
        ]
    
    def get_active_certifications(self, obj):
        return obj.certifications.filter(status='APPROVED').count()
    
    def get_supported_standards(self, obj):
        return list(obj.standards.filter(is_active=True).values_list('name', flat=True))

class CertificationSerializer(serializers.ModelSerializer):
    """Serializer para certificaciones"""
    certified_entity_name = serializers.CharField(source='certified_entity.username', read_only=True)
    standard_name = serializers.CharField(source='standard.name', read_only=True)
    auditor_name = serializers.CharField(source='auditor.username', read_only=True)
    animals_count = serializers.SerializerMethodField()
    is_valid = serializers.SerializerMethodField()
    
    class Meta:
        model = Certification
        fields = [
            'id', 'certificate_number', 'certified_entity_name', 'standard_name',
            'auditor_name', 'grade', 'score', 'issue_date', 'expiry_date',
            'status', 'animals_count', 'is_valid', 'blockchain_certificate'
        ]
    
    def get_animals_count(self, obj):
        return obj.animals.count()
    
    def get_is_valid(self, obj):
        return obj.is_valid

class CertificationStandardSerializer(serializers.ModelSerializer):
    """Serializer para estándares de certificación"""
    certification_body_name = serializers.CharField(source='certification_body.name', read_only=True)
    active_certifications = serializers.SerializerMethodField()
    
    class Meta:
        model = CertificationStandard
        fields = [
            'id', 'name', 'code', 'version', 'certification_body_name',
            'grading_system', 'minimum_score', 'validity_days',
            'active_certifications', 'is_active'
        ]
    
    def get_active_certifications(self, obj):
        return obj.certifications.filter(status='APPROVED').count()