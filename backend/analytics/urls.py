from django.urls import path, include
from .views import (
    GeneticAnalyticsView,
    HealthTrendsView,
    SupplyChainAnalyticsView,
    SustainabilityMetricsView,
    BlockchainAnalyticsView,
    SystemPerformanceView,
    PredictiveAnalyticsView,
    CustomReportView
)

urlpatterns = [
    # -------------------------------------------------------------------------
    # ANALYTICS GENÉTICOS
    # -------------------------------------------------------------------------
    path(
        'genetic/', 
        GeneticAnalyticsView.as_view(), 
        name='genetic-analytics',
        kwargs={'description': 'Analytics de composición genética y defectos por raza'}
    ),
    
    # -------------------------------------------------------------------------
    # TENDENCIAS DE SALUD
    # -------------------------------------------------------------------------
    path(
        'health-trends/', 
        HealthTrendsView.as_view(), 
        name='health-trends',
        kwargs={'description': 'Tendencias de salud y datos de sensores (últimos 30 días)'}
    ),
    path(
        'health-trends/<int:days>/', 
        HealthTrendsView.as_view(), 
        name='health-trends-days',
        kwargs={'description': 'Tendencias de salud con período personalizado'}
    ),
    
    # -------------------------------------------------------------------------
    # CADENA DE SUMINISTRO
    # -------------------------------------------------------------------------
    path(
        'supply-chain/', 
        SupplyChainAnalyticsView.as_view(), 
        name='supply-chain-analytics',
        kwargs={'description': 'Analytics de la cadena de suministro y logística'}
    ),
    
    # -------------------------------------------------------------------------
    # MÉTRICAS DE SOSTENIBILIDAD
    # -------------------------------------------------------------------------
    path(
        'sustainability/', 
        SustainabilityMetricsView.as_view(), 
        name='sustainability-metrics',
        kwargs={'description': 'Métricas de sostenibilidad ambiental y impacto'}
    ),
    
    # -------------------------------------------------------------------------
    # ANALYTICS DE BLOCKCHAIN
    # -------------------------------------------------------------------------
    path(
        'blockchain/', 
        BlockchainAnalyticsView.as_view(), 
        name='blockchain-analytics',
        kwargs={'description': 'Métricas de rendimiento de blockchain y transacciones'}
    ),
    path(
        'blockchain/<int:days>/', 
        BlockchainAnalyticsView.as_view(), 
        name='blockchain-analytics-days',
        kwargs={'description': 'Métricas de blockchain con período personalizado'}
    ),
    
    # -------------------------------------------------------------------------
    # RENDIMIENTO DEL SISTEMA
    # -------------------------------------------------------------------------
    path(
        'system-performance/', 
        SystemPerformanceView.as_view(), 
        name='system-performance',
        kwargs={'description': 'Métricas de rendimiento del sistema y infraestructura'}
    ),
    
    # -------------------------------------------------------------------------
    # ANALYTICS PREDICTIVOS
    # -------------------------------------------------------------------------
    path(
        'predictive/', 
        PredictiveAnalyticsView.as_view(), 
        name='predictive-analytics',
        kwargs={'description': 'Analytics predictivos y recomendaciones inteligentes'}
    ),
    
    # -------------------------------------------------------------------------
    # REPORTES PERSONALIZADOS
    # -------------------------------------------------------------------------
    path(
        'reports/custom/', 
        CustomReportView.as_view(), 
        name='custom-report',
        kwargs={'description': 'Reportes personalizados con múltiples métricas'}
    ),
    path(
        'reports/custom/<str:report_type>/', 
        CustomReportView.as_view(), 
        name='custom-report-type',
        kwargs={'description': 'Reportes personalizados por tipo específico'}
    ),
    path(
        'reports/custom/<str:report_type>/<int:days>/', 
        CustomReportView.as_view(), 
        name='custom-report-type-days',
        kwargs={'description': 'Reportes personalizados con tipo y período específicos'}
    ),
]

# Para incluir en el urls.py principal
app_name = 'analytics'

# Documentación de parámetros de query disponibles
ANALYTICS_QUERY_PARAMS = {
    'health-trends': {
        'days': 'Número de días para el análisis (default: 30)'
    },
    'blockchain': {
        'days': 'Número de días para el análisis (default: 30)'
    },
    'custom-report': {
        'type': 'Tipo de reporte (comprehensive, financial, operational)',
        'days': 'Número de días para el análisis (default: 30)'
    }
}

# Ejemplos de uso para documentación
ANALYTICS_API_EXAMPLES = {
    'genetic': {
        'analytics': '/api/analytics/genetic/'
    },
    'health': {
        'default': '/api/analytics/health-trends/',
        'custom_days': '/api/analytics/health-trends/60/'
    },
    'supply_chain': {
        'analytics': '/api/analytics/supply-chain/'
    },
    'sustainability': {
        'metrics': '/api/analytics/sustainability/'
    },
    'blockchain': {
        'default': '/api/analytics/blockchain/',
        'custom_days': '/api/analytics/blockchain/90/'
    },
    'performance': {
        'system': '/api/analytics/system-performance/'
    },
    'predictive': {
        'analytics': '/api/analytics/predictive/'
    },
    'reports': {
        'comprehensive': '/api/analytics/reports/custom/comprehensive/',
        'financial': '/api/analytics/reports/custom/financial/30/',
        'operational': '/api/analytics/reports/custom/operational/'
    }
}

# Versión con router para posibles expansiones futuras
analytics_urlpatterns = urlpatterns

# Si en el futuro necesitas versionado de API
versioned_patterns = [
    path('v1/', include((analytics_urlpatterns, 'analytics-v1'))),
]

# Para incluir en el urls.py principal de Django:
# path('api/analytics/', include('analytics.urls')),