# backend/certification/models.py
from django.db import models
from django.core.exceptions import ValidationError
from core.multichain.models import SmartContractAbstract, ChainSpecificModel
from core.multichain.manager import multichain_manager
# ❌ ELIMINAR: from core.multichain.adapters import MultichainAdapterMixin
# ✅ USAR TU ADAPTER EXISTENTE
from .adapters.multichain_adapter import CertificationMultichainAdapter
import json
from datetime import timedelta
from django.utils import timezone

class CertificationContract(SmartContractAbstract):
    """Contrato inteligente para gestión de certificaciones"""
    CONTRACT_TYPES = [
        ('CERT_REGISTRY', 'Registro de Certificaciones'),
        ('AUDITOR_REGISTRY', 'Registro de Auditores'),
        ('STANDARD_REGISTRY', 'Registro de Estándares'),
    ]
    
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPES)
    supports_erc_1484 = models.BooleanField(default=False, verbose_name="Soporta ERC-1484")
    supports_erc_1888 = models.BooleanField(default=False, verbose_name="Soporta ERC-1888")
    
    # Configuración específica
    max_certifications = models.IntegerField(default=1000, verbose_name="Máximo de Certificaciones")
    certification_fee = models.DecimalField(max_digits=20, decimal_places=18, null=True, blank=True, verbose_name="Tarifa de Certificación")
    
    class Meta:
        verbose_name = "Contrato de Certificación"
        verbose_name_plural = "Contratos de Certificación"

class StarknetCertificationContract(CertificationContract):
    """Implementación específica para Starknet"""
    class_hash = models.CharField(max_length=255, unique=True)
    supports_cairo_standards = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Contrato de Certificación Starknet"
        verbose_name_plural = "Contratos de Certificación Starknet"

class GlobalCertificationBody(models.Model):
    """Organismos de certificación global - INTEGRADO CON USUARIOS EXISTENTES"""
    
    CERTIFICATION_TYPES = [
        ('ORGANIC', 'Orgánico'),
        ('ANIMAL_WELFARE', 'Bienestar Animal'),
        ('SUSTAINABILITY', 'Sostenibilidad'),
        ('FOOD_SAFETY', 'Inocuidad Alimentaria'),
        ('ORIGIN', 'Denominación de Origen'),
        ('QUALITY', 'Calidad Premium'),
        ('CARBON_CREDIT', 'Créditos de Carbono'),
    ]
    
    # VINCULACIÓN CON USUARIO EXISTENTE (usando tu estructura actual)
    admin_user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='managed_certification_bodies',
        limit_choices_to={'role__in': ['AUDITOR', 'ADMIN', 'CERTIFICATION_BODY']},
        verbose_name="Usuario Administrador"
    )
    
    # CAMPOS EXISTENTES (MANTENIENDO TU ESTRUCTURA)
    name = models.CharField(max_length=200, verbose_name="Nombre del Organismo")
    acronym = models.CharField(max_length=20, verbose_name="Sigla")
    description = models.TextField(verbose_name="Descripción")
    certification_type = models.CharField(max_length=20, choices=CERTIFICATION_TYPES, verbose_name="Tipo de Certificación")
    website = models.URLField(blank=True, verbose_name="Sitio Web")
    country = models.CharField(max_length=100, verbose_name="País de Origen")
    international_scope = models.BooleanField(default=False, verbose_name="Alcance Internacional")
    
    # NUEVOS CAMPOS PARA MEJOR INTEGRACIÓN
    accreditation_number = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name="Número de Acreditación",
        help_text="Número oficial de acreditación del organismo",
        blank=True
    )
    legal_name = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name="Razón Social"
    )
    
    # Estándares reconocidos (manteniendo tu estructura)
    recognized_standards = models.JSONField(
        default=list,
        verbose_name="Estándares Reconocidos",
        help_text="Lista de estándares internacionales reconocidos"
    )
    
    # MEJORAR CONFIGURACIÓN BLOCKCHAIN (usando tus redes)
    issues_blockchain_certs = models.BooleanField(
        default=True, 
        verbose_name="Emite Certificados Blockchain"
    )
    
    # USAR TUS REDES CONFIGURADAS EN .env
    preferred_networks = models.JSONField(
        default=list,
        verbose_name="Redes Preferidas",
        help_text="Redes blockchain donde emite certificados"
    )
    
    supported_countries = models.JSONField(
        default=list,
        verbose_name="Países Soportados",
        blank=True
    )
    
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Organismo de Certificación Global"
        verbose_name_plural = "Organismos de Certificación Global"
        ordering = ['name']
        indexes = [
            models.Index(fields=['certification_type']),
            models.Index(fields=['international_scope']),
            models.Index(fields=['is_active']),
            models.Index(fields=['accreditation_number']),
        ]

    def __str__(self):
        return f"{self.name} ({self.acronym})"
    
    def clean(self):
        super().clean()
        if self.international_scope and not self.country:
            raise ValidationError("Los organismos internacionales deben especificar país de origen")
        
        # VALIDAR USUARIO ADMINISTRADOR
        if self.admin_user and self.admin_user.role not in ['AUDITOR', 'ADMIN', 'CERTIFICATION_BODY']:
            raise ValidationError({
                'admin_user': 'El usuario debe ser AUDITOR, ADMIN o CERTIFICATION_BODY'
            })
    
    def save(self, *args, **kwargs):
        # CONFIGURACIÓN AUTOMÁTICA DE REDES PREFERIDAS (usando tus redes)
        if not self.preferred_networks and self.issues_blockchain_certs:
            # Usar las redes de tu .env por defecto
            self.preferred_networks = ['POLYGON', 'STARKNET']
        
        # Generar número de acreditación si no existe
        if not self.accreditation_number:
            self.accreditation_number = f"ACCR-{self.name[:4].upper()}-{timezone.now().strftime('%Y%m%d')}"
        
        super().save(*args, **kwargs)
    
    # NUEVAS PROPIEDADES
    @property
    def issued_certificates_count(self):
        """Contar certificados emitidos"""
        from django.db.models import Count, Q
        return self.standards.aggregate(
            total=Count('certifications', filter=Q(certifications__status='APPROVED'))
        )['total'] or 0
    
    @property
    def active_auditors(self):
        """Obtener auditores activos vinculados"""
        from users.models import User
        return User.objects.filter(
            role='AUDITOR',
            is_active=True
        )[:10]

# ❌ ELIMINAR MultichainAdapterMixin - USAR MÉTODOS DIRECTOS
class CertificationStandard(models.Model):
    """Estándares de certificación - MEJORADO"""
    
    GRADING_SYSTEMS = [
        ('LETTER', 'Sistema de Letras (A, B, C)'),
        ('SCORE', 'Sistema de Puntuación (1-100)'),
        ('STAR', 'Sistema de Estrellas (1-5)'),
        ('BINARY', 'Aprobado/No Aprobado'),
    ]
    
    certification_body = models.ForeignKey(
        GlobalCertificationBody, 
        on_delete=models.CASCADE, 
        related_name='standards'
    )
    
    # MANTENER TUS CAMPOS EXISTENTES
    name = models.CharField(max_length=100, verbose_name="Nombre del Estándar")
    code = models.CharField(max_length=50, verbose_name="Código del Estándar")
    description = models.TextField(verbose_name="Descripción")
    version = models.CharField(max_length=20, default="1.0", verbose_name="Versión")
    
    # Sistema de calificación
    grading_system = models.CharField(max_length=10, choices=GRADING_SYSTEMS, verbose_name="Sistema de Calificación")
    passing_score = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name="Puntuación Mínima"
    )
    
    # MEJORAR ESTRUCTURA DE REQUISITOS
    requirements = models.JSONField(
        default=dict,
        verbose_name="Requisitos de Certificación",
        help_text="Estructura JSON con criterios y puntuaciones"
    )
    
    # Validez y renovación
    validity_days = models.IntegerField(default=365, verbose_name="Validez (días)")
    requires_renewal = models.BooleanField(default=True, verbose_name="Requiere Renovación")
    renewal_notice_days = models.IntegerField(default=30, verbose_name="Aviso de Renovación (días antes)")
    
    # NUEVOS CAMPOS PARA AUDITORÍA
    requires_audit = models.BooleanField(default=True, verbose_name="Requiere Auditoría")
    audit_frequency_days = models.IntegerField(default=180, verbose_name="Frecuencia de Auditoría (días)")
    
    # Configuración multichain
    blockchain_template = models.JSONField(
        default=dict,
        verbose_name="Plantilla Blockchain",
        help_text="Estructura para certificados en blockchain"
    )
    
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Estándar de Certificación"
        verbose_name_plural = "Estándares de Certificación"
        ordering = ['certification_body', 'name']
        unique_together = ['certification_body', 'code', 'version']
        indexes = [
            models.Index(fields=['code', 'version']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.code} v{self.version} - {self.name}"
    
    def clean(self):
        super().clean()
        # VALIDACIONES MEJORADAS
        if self.passing_score and (self.passing_score < 0 or self.passing_score > 100):
            raise ValidationError({'passing_score': 'La puntuación mínima debe estar entre 0 y 100'})
    
    # NUEVAS PROPIEDADES
    @property
    def full_code(self):
        return f"{self.certification_body.accreditation_number}-{self.code}-v{self.version}"
    
    def calculate_grade(self, score):
        """Calcular grado basado en el sistema de calificación"""
        if score is None:
            return 'N/A'
            
        score = float(score)
        
        if self.grading_system == 'LETTER':
            if score >= 90: return 'A'
            elif score >= 75: return 'B'
            elif score >= 60: return 'C'
            else: return 'F'
        elif self.grading_system == 'BINARY':
            return 'P' if score >= float(self.passing_score) else 'F'
        elif self.grading_system == 'STAR':
            stars = round((score / 100) * 5)
            return str(stars)
        else:  # SCORE
            return f"{score:.1f}"

# ❌ ELIMINAR MultichainAdapterMixin - USAR TU ADAPTER DIRECTAMENTE
class Certification(models.Model):
    """Certificación multinivel - MEJORADO CON INTEGRACIÓN MULTICHAIN"""
    
    STATUS_CHOICES = [
        ('DRAFT', 'Borrador'),
        ('PENDING', 'Pendiente de Aprobación'),
        ('APPROVED', 'Aprobada'),
        ('REJECTED', 'Rechazada'),
        ('EXPIRED', 'Expirada'),
        ('REVOKED', 'Revocada'),
        ('SUSPENDED', 'Suspendida'),
    ]
    
    GRADES = [
        ('A', 'Grado A - Excelente'),
        ('B', 'Grado B - Bueno'),
        ('C', 'Grado C - Básico'),
        ('P', 'Aprobado'),
        ('F', 'No Aprobado'),
    ]
    
    SCOPE_CHOICES = [
        ('GLOBAL', 'Global (Toda la operación)'),
        ('BATCH', 'Por Lote'),
        ('ANIMAL', 'Por Animal'),
        ('PRODUCT', 'Por Producto'),
    ]
    
    # MANTENER TUS RELACIONES EXISTENTES
    certified_entity = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE, 
        related_name='certifications'
    )
    standard = models.ForeignKey(
        CertificationStandard, 
        on_delete=models.CASCADE, 
        related_name='certifications'
    )
    
    # AÑADIR ALCANCE DE CERTIFICACIÓN
    scope_type = models.CharField(
        max_length=10, 
        choices=SCOPE_CHOICES, 
        default='GLOBAL', 
        verbose_name="Alcance"
    )
    
    # RELACIÓN CON ANIMALES Y LOTES (usando tus modelos existentes)
    animals = models.ManyToManyField(
        'cattle.Animal',
        related_name='certification_certifications',
        blank=True,
        verbose_name="Animales Certificados"
    )
    
    batches = models.ManyToManyField(
        'cattle.Batch',
        related_name='certifications',
        blank=True,
        verbose_name="Lotes Certificados"
    )
    
    # INFORMACIÓN DE LA CERTIFICACIÓN (TUS CAMPOS EXISTENTES)
    certificate_number = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name="Número de Certificado",
        blank=True  # Se generará automáticamente
    )
    grade = models.CharField(max_length=1, choices=GRADES, verbose_name="Grado")
    score = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name="Puntuación"
    )
    issue_date = models.DateField(verbose_name="Fecha de Emisión")
    expiry_date = models.DateField(verbose_name="Fecha de Expiración")
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='DRAFT', 
        verbose_name="Estado"
    )
    
    # MEJORAR AUDITOR Y EVALUACIÓN
    auditor = models.ForeignKey(
        'users.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='audited_certifications', 
        verbose_name="Auditor",
        limit_choices_to={'role': 'AUDITOR'}
    )
    audit_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Auditoría")
    audit_report = models.TextField(blank=True, verbose_name="Informe de Auditoría")
    
    # NUEVOS CAMPOS DE CONTROL
    next_audit_due = models.DateField(null=True, blank=True, verbose_name="Próxima Auditoría")
    renewal_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Renovación")
    suspension_reason = models.TextField(blank=True, verbose_name="Motivo de Suspensión")
    revocation_cause = models.TextField(blank=True, verbose_name="Causa de Revocación")
    
    # PERSONAL ADICIONAL INVOLUCRADO
    approved_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_certifications',
        limit_choices_to={'role__in': ['ADMIN', 'AUDITOR']},
        verbose_name="Aprobado por"
    )
    
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_certifications',
        verbose_name="Creado por"
    )
    
    # Evidencia y documentos (TU CAMPO EXISTENTE)
    supporting_documents = models.JSONField(
        default=list,
        verbose_name="Documentos de Soporte",
        help_text="Lista de URLs o hashes de documentos"
    )
    
    # Metadatos blockchain MULTICHAIN (TUS CAMPOS EXISTENTES)
    blockchain_certificate = models.BooleanField(default=False, verbose_name="Certificado en Blockchain")
    multichain_data = models.OneToOneField(
        'core.ChainSpecificModel', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Datos Multichain"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Certificación"
        verbose_name_plural = "Certificaciones"
        ordering = ['-issue_date']
        indexes = [
            models.Index(fields=['certified_entity', 'status']),
            models.Index(fields=['standard', 'grade']),
            models.Index(fields=['expiry_date']),
            models.Index(fields=['status']),
            models.Index(fields=['scope_type']),
            models.Index(fields=['blockchain_certificate']),
        ]

    def __str__(self):
        return f"Cert {self.certificate_number} - {self.certified_entity.username} - {self.standard.code}"
    
    def clean(self):
        super().clean()
        if self.issue_date and self.expiry_date and self.issue_date >= self.expiry_date:
            raise ValidationError("La fecha de expiración debe ser posterior a la fecha de emisión")
        
        # VALIDACIONES ADICIONALES
        if self.scope_type == 'ANIMAL' and not self.animals.exists():
            raise ValidationError({
                'animals': 'La certificación por animal requiere especificar animales'
            })
        
        if self.scope_type == 'BATCH' and not self.batches.exists():
            raise ValidationError({
                'batches': 'La certificación por lote requiere especificar lotes'
            })
    
    def save(self, *args, **kwargs):
        # GENERAR NÚMERO DE CERTIFICADO AUTOMÁTICAMENTE
        if not self.certificate_number:
            self.certificate_number = self.generate_certificate_number()
        
        # CALCULAR GRADO AUTOMÁTICAMENTE
        if self.score and not self.grade:
            self.grade = self.standard.calculate_grade(float(self.score))
        
        # CALCULAR FECHAS AUTOMÁTICAMENTE
        if self.status == 'APPROVED':
            if self.audit_date and not self.next_audit_due:
                self.next_audit_due = self.audit_date + timedelta(
                    days=self.standard.audit_frequency_days
                )
            
            if self.expiry_date and not self.renewal_date:
                self.renewal_date = self.expiry_date - timedelta(days=30)
        
        super().save(*args, **kwargs)
    
    def generate_certificate_number(self):
        """Generar número de certificado único"""
        timestamp = timezone.now().strftime("%Y%m%d")
        body_code = self.standard.certification_body.accreditation_number[:4].upper()
        entity_id = str(self.certified_entity.id).zfill(6)[-4:]
        sequential = Certification.objects.filter(
            standard__certification_body=self.standard.certification_body,
            created_at__date=timezone.now().date()
        ).count() + 1
        
        return f"CERT-{body_code}-{timestamp}-{entity_id}-{sequential:03d}"
    
    @property
    def is_valid(self):
        """Verificar si la certificación es válida"""
        return (self.status == 'APPROVED' and 
                self.expiry_date > timezone.now().date())
    
    @property
    def days_until_expiry(self):
        """Días hasta la expiración"""
        if self.expiry_date:
            return (self.expiry_date - timezone.now().date()).days
        return None
    
    # NUEVAS PROPIEDADES
    @property
    def requires_renewal(self):
        """Verificar si requiere renovación"""
        return (self.is_valid and 
                self.days_until_expiry is not None and 
                self.days_until_expiry <= 30)
    
    @property
    def is_compliant(self):
        """Verificar si cumple con todos los requisitos"""
        return (self.is_valid and 
                self.score and 
                float(self.score) >= float(self.standard.passing_score))
    
    def get_certified_animals_info(self):
        """Obtener información de animales certificados"""
        if self.scope_type == 'ANIMAL' and self.animals.exists():
            return {
                'total_animals': self.animals.count(),
                'species': list(self.animals.values_list('species', flat=True).distinct()),
                'average_age': self.animals.aggregate(models.Avg('age'))
            }
        return None
    
    # ✅ USAR TU ADAPTER EXISTENTE EN LUGAR DEL MIXIN
    @property
    def multichain_adapter(self):
        """Acceder al adaptador multichain específico para certificaciones"""
        return CertificationMultichainAdapter(self)
    
    def issue_on_blockchain(self, networks=None):
        """Emitir certificación en blockchain usando TU adapter"""
        return self.multichain_adapter.issue_on_blockchain(networks)
    
    def verify_blockchain_integrity(self):
        """Verificar integridad en blockchain usando TU adapter"""
        if not self.blockchain_certificate:
            return {'verified': False, 'reason': 'Not issued on blockchain'}
            
        try:
            # Aquí integrarías la verificación real con tu adapter
            # Por ahora simulación
            verification_data = {
                'verified': True,
                'networks': self.standard.certification_body.preferred_networks,
                'timestamp': timezone.now().isoformat(),
                'certificate_hash': f"0x{hash(self.certificate_number)[:16]}"
            }
            
            return verification_data
            
        except Exception as e:
            return {'verified': False, 'error': str(e)}

class CertificationAuditTrail(models.Model):
    """Auditoría de cambios en certificaciones - MANTENIENDO TU ESTRUCTURA EXISTENTE"""
    certification = models.ForeignKey(Certification, on_delete=models.CASCADE, related_name='audit_trail')
    action = models.CharField(max_length=50, verbose_name="Acción")
    performed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, verbose_name="Realizado por")
    previous_state = models.JSONField(verbose_name="Estado Anterior")
    new_state = models.JSONField(verbose_name="Nuevo Estado")
    notes = models.TextField(blank=True, verbose_name="Notas")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora")
    
    # NUEVO CAMPO PARA BLOCKCHAIN
    blockchain_hash = models.CharField(
        max_length=255, 
        blank=True, 
        verbose_name="Hash Blockchain"
    )

    class Meta:
        verbose_name = "Registro de Auditoría de Certificación"
        verbose_name_plural = "Registros de Auditoría de Certificación"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['certification', 'timestamp']),
        ]

    def __str__(self):
        return f"Auditoría {self.certification.certificate_number} - {self.action}"

# NUEVO MODELO PARA AUDITORÍAS DETALLADAS (COMPLEMENTARIO)
class CertificationAudit(models.Model):
    """Auditorías detalladas de certificación - NUEVO MODELO COMPLEMENTARIO"""
    
    AUDIT_TYPES = [
        ('INITIAL', 'Auditoría Inicial'),
        ('RENEWAL', 'Auditoría de Renovación'),
        ('FOLLOW_UP', 'Auditoría de Seguimiento'),
        ('UNSCHEDULED', 'Auditoría No Programada'),
    ]
    
    certification = models.ForeignKey(
        Certification, 
        on_delete=models.CASCADE, 
        related_name='detailed_audits'
    )
    audit_type = models.CharField(
        max_length=12,
        choices=AUDIT_TYPES,
        default='INITIAL',
        verbose_name="Tipo de Auditoría"
    )
    audit_date = models.DateField(verbose_name="Fecha de Auditoría")
    auditor = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'AUDITOR'},
        verbose_name="Auditor"
    )
    score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Puntuación")
    findings = models.JSONField(default=dict, verbose_name="Hallazgos")
    recommendations = models.TextField(verbose_name="Recomendaciones")
    compliance_level = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        verbose_name="Nivel de Cumplimiento (%)"
    )
    blockchain_hash = models.CharField(max_length=255, blank=True, verbose_name="Hash Blockchain")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Auditoría Detallada de Certificación"
        verbose_name_plural = "Auditorías Detalladas de Certificación"
        ordering = ['-audit_date']

    def __str__(self):
        return f"Auditoría {self.certification.certificate_number} - {self.audit_date}"
    
    def save(self, *args, **kwargs):
        # Actualizar la certificación con los resultados de la auditoría
        if self.pk is None:  # Solo para nuevas auditorías
            self.certification.score = self.score
            self.certification.audit_date = self.audit_date
            self.certification.grade = self.certification.standard.calculate_grade(float(self.score))
            self.certification.save()
        
        super().save(*args, **kwargs)