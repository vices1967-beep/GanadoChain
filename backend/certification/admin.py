# backend/certification/admin.py - CORREGIDO
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    GlobalCertificationBody, CertificationStandard, 
    Certification, CertificationAudit
)

@admin.register(GlobalCertificationBody)
class GlobalCertificationBodyAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'accreditation_number', 'certification_type', 
        'country', 'international_scope',  
        'is_active', 'issued_certificates_count'
    ]
    list_filter = ['certification_type', 'international_scope', 'is_active']
    search_fields = ['name', 'accreditation_number', 'country']
    readonly_fields = ['issued_certificates_count']
    filter_horizontal = []  # ← CORREGIDO: preferred_networks no es ManyToMany
    
    fieldsets = (
        ('Información de la Organización', {
            'fields': ['admin_user', 'name', 'legal_name', 'accreditation_number']  # ← CORREGIDO: lista
        }),
        ('Alcance y Capacidades', {
            'fields': ['certification_type', 'country', 'international_scope', 'supported_countries']  # ← CORREGIDO: lista
        }),
        ('Estándares Reconocidos', {
            'fields': ['recognized_standards']  # ← CORREGIDO: lista
        }),
        ('Configuración Blockchain', {
            'fields': ['preferred_networks']  # ← CORREGIDO: lista
        }),
        ('Estado', {
            'fields': ['is_active', 'created_at', 'updated_at']  # ← CORREGIDO: lista
        })
    )

@admin.register(CertificationStandard)
class CertificationStandardAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'code', 'version', 'certification_body', 
        'grading_system', 'is_active'
    ]
    list_filter = ['certification_body', 'grading_system', 'is_active']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['full_code']
    
    fieldsets = (
        ('Información del Estándar', {
            'fields': ['certification_body', 'name', 'code', 'version', 'description']  # ← CORREGIDO: lista
        }),
        ('Sistema de Evaluación', {
            'fields': ['grading_system', 'criteria']  # ← CORREGIDO: lista
        }),
        ('Validez y Auditoría', {
            'fields': ['validity_days', 'requires_audit', 'audit_frequency_days']  # ← CORREGIDO: lista
        }),
        ('Configuración Blockchain', {
            'fields': ['blockchain_template']  # ← CORREGIDO: lista
        }),
        ('Estado', {
            'fields': ['is_active', 'created_at', 'updated_at']  # ← CORREGIDO: lista
        })
    )

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = [
        'certificate_number', 'certified_entity', 'standard',
        'status', 'issue_date', 'expiry_date',  # ← CORREGIDO: removido final_grade
        'is_valid', 'blockchain_certificate', 'days_until_expiry_display'
    ]
    list_filter = [
        'standard', 'status', 'scope_type',  # ← CORREGIDO: removido final_grade
        'blockchain_certificate', 'issue_date'
    ]
    search_fields = [
        'certificate_number', 'certified_entity__username',
        'standard__name', 'auditor__username'
    ]
    readonly_fields = [
        'certificate_number', 'is_valid', 'days_until_expiry',
        'requires_renewal', 'is_compliant'
    ]
    filter_horizontal = ['animals', 'batches']
    date_hierarchy = 'issue_date'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ['certified_entity', 'standard', 'certificate_number', 'scope_type']  # ← CORREGIDO: lista
        }),
        ('Alcance de Certificación', {
            'fields': ['animals', 'batches']  # ← CORREGIDO: lista
        }),
        ('Resultados de Evaluación', {
            'fields': ['audit_score', 'audit_report']  # ← CORREGIDO: removido final_grade
        }),
        ('Fechas Críticas', {
            'fields': ['issue_date', 'expiry_date', 'last_audit_date', 'next_audit_due', 'renewal_date']  # ← CORREGIDO: lista
        }),
        ('Personal Involucrado', {
            'fields': ['auditor', 'approved_by', 'created_by']  # ← CORREGIDO: lista (y cambiado assigned_auditor por auditor)
        }),
        ('Estado y Controles', {
            'fields': ['status', 'suspension_reason', 'revocation_cause']  # ← CORREGIDO: lista
        }),
        ('Integración Blockchain', {
            'fields': ['blockchain_certificate', 'multichain_data']  # ← CORREGIDO: lista
        }),
        ('Propiedades Calculadas', {
            'fields': ['is_valid', 'days_until_expiry', 'requires_renewal', 'is_compliant']  # ← CORREGIDO: lista
        }),
        ('Documentación', {
            'fields': ['supporting_documents']  # ← CORREGIDO: lista
        })
    )
    
    def days_until_expiry_display(self, obj):
        days = obj.days_until_expiry
        if days is None:
            return "N/A"
        color = "green" if days > 30 else "orange" if days > 0 else "red"
        return format_html(f'<span style="color: {color};">{days} días</span>')
    days_until_expiry_display.short_description = 'Días hasta expiración'

@admin.register(CertificationAudit)
class CertificationAuditAdmin(admin.ModelAdmin):
    list_display = [
        'certification', 'audit_type', 'auditor', 'audit_date',
        'score', 'compliance_level'
    ]
    list_filter = ['audit_type', 'audit_date']
    search_fields = ['certification__certificate_number', 'auditor__username']
    date_hierarchy = 'audit_date'
    
    fieldsets = (
        ('Información de Auditoría', {
            'fields': ['certification', 'audit_type', 'audit_date', 'auditor']  # ← CORREGIDO: lista
        }),
        ('Resultados', {
            'fields': ['score', 'findings', 'recommendations', 'compliance_level']  # ← CORREGIDO: lista
        }),
        ('Acciones Correctivas', {
            'fields': ['corrective_actions', 'next_follow_up']  # ← CORREGIDO: lista
        }),
        ('Blockchain', {
            'fields': ['blockchain_hash']  # ← CORREGIDO: lista
        })
    )