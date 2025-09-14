from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ComplianceReportView,
    ExportAnimalDataView,
    AuditReportGenerator,
    FinancialReportView,
    SystemHealthReportView,
    ExportReportView
)

# Router para endpoints que podrían convertirse en ViewSets en el futuro
router = DefaultRouter()

# Aquí puedes registrar ViewSets si los creas en el futuro
# router.register('compliance', ComplianceViewSet, basename='compliance-report')
# router.register('audit', AuditViewSet, basename='audit-report')

urlpatterns = [
    # -------------------------------------------------------------------------
    # REPORTES DE CUMPLIMIENTO (Compatibles con parámetros de query)
    # -------------------------------------------------------------------------
    path(
        'compliance/',
        ComplianceReportView.as_view(),
        name='compliance-report',
        kwargs={'description': 'Reporte general de cumplimiento y certificaciones. Parámetros: type, days'}
    ),
    
    # -------------------------------------------------------------------------
    # EXPORTACIÓN DE DATOS DE ANIMALES
    # -------------------------------------------------------------------------
    path(
        'export/animals/',
        ExportAnimalDataView.as_view(),
        name='export-animal-data',
        kwargs={'description': 'Exportar datos de animales. Parámetros: format, animal_ids[]'}
    ),
    
    # -------------------------------------------------------------------------
    # REPORTES DE AUDITORÍA
    # -------------------------------------------------------------------------
    path(
        'audit/',
        AuditReportGenerator.as_view(),
        name='audit-report',
        kwargs={'description': 'Reporte de auditoría del sistema. Parámetros: type, days'}
    ),
    
    # -------------------------------------------------------------------------
    # REPORTES FINANCIEROS
    # -------------------------------------------------------------------------
    path(
        'financial/',
        FinancialReportView.as_view(),
        name='financial-report',
        kwargs={'description': 'Reporte financiero. Parámetro: days'}
    ),
    
    # -------------------------------------------------------------------------
    # REPORTE DE SALUD DEL SISTEMA
    # -------------------------------------------------------------------------
    path(
        'system-health/',
        SystemHealthReportView.as_view(),
        name='system-health-report',
        kwargs={'description': 'Reporte completo de salud del sistema'}
    ),
    
    # -------------------------------------------------------------------------
    # EXPORTACIÓN DE REPORTES COMPLETOS
    # -------------------------------------------------------------------------
    path(
        'export/report/',
        ExportReportView.as_view(),
        name='export-report',
        kwargs={'description': 'Exportar reportes. Parámetros: type, format'}
    ),
    
    # -------------------------------------------------------------------------
    # ENDPOINTS DE API CON ROUTER (para versionado y futuras expansiones)
    # -------------------------------------------------------------------------
    path('api/v1/', include(router.urls), name='reports-api'),
    
    # -------------------------------------------------------------------------
    # ENDPOINTS ESPECÍFICOS PARA INTEGRACIÓN CON OTRAS APPS
    # -------------------------------------------------------------------------
    path(
        'api/compliance/quick/',
        ComplianceReportView.as_view(),
        name='api-compliance-quick',
        kwargs={'description': 'API rápida para reportes de cumplimiento'}
    ),
    path(
        'api/audit/summary/',
        AuditReportGenerator.as_view(),
        name='api-audit-summary',
        kwargs={'description': 'Resumen de auditoría para dashboards'}
    ),
]

# Para incluir en el urls.py principal
app_name = 'reports'

# Documentación de parámetros disponibles
REPORT_PARAMETERS_DOCS = {
    'compliance': {
        'type': ['general', 'certifications', 'health', 'blockchain', 'iot', 'rewards'],
        'days': 'Número de días (default: 30)'
    },
    'export_animals': {
        'format': ['json', 'csv'],
        'animal_ids': 'Lista de IDs de animales separados por coma'
    },
    'audit': {
        'type': ['general', 'user_activity', 'action_types', 'blockchain_audit'],
        'days': 'Número de días (default: 7)'
    },
    'financial': {
        'days': 'Número de días (default: 30)'
    },
    'export_report': {
        'type': ['compliance', 'financial'],
        'format': ['json', 'csv']
    }
}

# Ejemplos de uso para documentación
API_USAGE_EXAMPLES = {
    'compliance': {
        'general': '/reports/compliance/?type=general&days=30',
        'certifications': '/reports/compliance/?type=certifications&days=60',
        'json_response': '/reports/compliance/?type=health&format=json'
    },
    'export': {
        'animals_csv': '/reports/export/animals/?format=csv',
        'animals_json': '/reports/export/animals/?format=json&animal_ids=1,2,3',
        'report_financial': '/reports/export/report/?type=financial&format=csv'
    },
    'api_endpoints': {
        'compliance_quick': '/reports/api/compliance/quick/?type=blockchain',
        'audit_summary': '/reports/api/audit/summary/?type=user_activity'
    }
}