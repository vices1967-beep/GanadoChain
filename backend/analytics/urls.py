from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GeneticAnalyticsView,
    HealthTrendsView,
    SupplyChainAnalyticsView,
    SustainabilityMetricsView,
    BlockchainAnalyticsView,
    SystemPerformanceView,
    PredictiveAnalyticsView,
    CustomReportView,
    ConsumerAnalyticsViewSet,
    CarbonFootprintViewSet
)

app_name = 'analytics'

router = DefaultRouter()
# Nuevos endpoints con ViewSets
router.register(r'consumer-analytics', ConsumerAnalyticsViewSet, basename='consumeranalytics')
router.register(r'carbon-footprint', CarbonFootprintViewSet, basename='carbonfootprint')

# URLs basadas en clases (existente)
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
    
    # -------------------------------------------------------------------------
    # INCLUIR RUTAS DEL ROUTER (nuevos endpoints)
    # -------------------------------------------------------------------------
    path('', include(router.urls)),
]

# Documentación de parámetros de query disponibles (expandida)
ANALYTICS_QUERY_PARAMS = {
    'health-trends': {
        'days': 'Número de días para el análisis (default: 30)',
        'animal_id': 'Filtrar por animal específico',
        'batch_id': 'Filtrar por lote específico'
    },
    'blockchain': {
        'days': 'Número de días para el análisis (default: 30)',
        'network': 'Filtrar por red blockchain específica',
        'user_id': 'Filtrar por usuario específico'
    },
    'custom-report': {
        'type': 'Tipo de reporte (comprehensive, financial, operational)',
        'days': 'Número de días para el análisis (default: 30)',
        'format': 'Formato de salida (json, csv, pdf)'
    },
    'consumer-analytics': {
        'start_date': 'Fecha de inicio (YYYY-MM-DD)',
        'end_date': 'Fecha de fin (YYYY-MM-DD)',
        'tier': 'Filtrar por nivel de consumidor'
    },
    'carbon-footprint': {
        'animal_id': 'Filtrar por animal específico',
        'batch_id': 'Filtrar por lote específico',
        'time_range': 'Rango de tiempo (day, week, month, year)'
    }
}

# Ejemplos de uso para documentación (expandida)
ANALYTICS_API_EXAMPLES = {
    'genetic': {
        'analytics': '/api/analytics/genetic/'
    },
    'health': {
        'default': '/api/analytics/health-trends/',
        'custom_days': '/api/analytics/health-trends/60/',
        'filtered': '/api/analytics/health-trends/?animal_id=123&days=90'
    },
    'supply_chain': {
        'analytics': '/api/analytics/supply-chain/'
    },
    'sustainability': {
        'metrics': '/api/analytics/sustainability/'
    },
    'blockchain': {
        'default': '/api/analytics/blockchain/',
        'custom_days': '/api/analytics/blockchain/90/',
        'filtered': '/api/analytics/blockchain/?network=STARKNET&days=30'
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
    },
    'consumer': {
        'analytics': '/api/analytics/consumer-analytics/',
        'stats': '/api/analytics/consumer-analytics/stats/',
        'filtered': '/api/analytics/consumer-analytics/?start_date=2024-01-01&end_date=2024-03-01'
    },
    'carbon': {
        'footprint': '/api/analytics/carbon-footprint/',
        'summary': '/api/analytics/carbon-footprint/summary/',
        'by_animal': '/api/analytics/carbon-footprint/by_animal/?animal_id=123'
    }
}

# Mapa completo de endpoints para documentación
ANALYTICS_ENDPOINTS_MAP = {
    'genetic_analytics': {
        'path': '/api/analytics/genetic/',
        'method': 'GET',
        'description': 'Analytics de composición genética y defectos por raza',
        'parameters': {}
    },
    'health_trends': {
        'path': '/api/analytics/health-trends/',
        'method': 'GET', 
        'description': 'Tendencias de salud y datos de sensores',
        'parameters': {
            'days': 'int (opcional)',
            'animal_id': 'int (opcional)',
            'batch_id': 'int (opcional)'
        }
    },
    'supply_chain_analytics': {
        'path': '/api/analytics/supply-chain/',
        'method': 'GET',
        'description': 'Analytics de la cadena de suministro y logística',
        'parameters': {}
    },
    'sustainability_metrics': {
        'path': '/api/analytics/sustainability/',
        'method': 'GET',
        'description': 'Métricas de sostenibilidad ambiental y impacto',
        'parameters': {}
    },
    'blockchain_analytics': {
        'path': '/api/analytics/blockchain/',
        'method': 'GET',
        'description': 'Métricas de rendimiento de blockchain y transacciones',
        'parameters': {
            'days': 'int (opcional)',
            'network': 'str (opcional)',
            'user_id': 'int (opcional)'
        }
    },
    'system_performance': {
        'path': '/api/analytics/system-performance/',
        'method': 'GET',
        'description': 'Métricas de rendimiento del sistema y infraestructura',
        'parameters': {}
    },
    'predictive_analytics': {
        'path': '/api/analytics/predictive/',
        'method': 'GET',
        'description': 'Analytics predictivos y recomendaciones inteligentes',
        'parameters': {}
    },
    'custom_reports': {
        'path': '/api/analytics/reports/custom/',
        'method': 'GET',
        'description': 'Reportes personalizados con múltiples métricas',
        'parameters': {
            'type': 'str (opcional)',
            'days': 'int (opcional)',
            'format': 'str (opcional)'
        }
    },
    'consumer_analytics_crud': {
        'path': '/api/analytics/consumer-analytics/',
        'method': 'GET, POST, PUT, DELETE',
        'description': 'CRUD completo para analytics de consumidores',
        'parameters': {
            'start_date': 'str (opcional)',
            'end_date': 'str (opcional)', 
            'tier': 'str (opcional)'
        }
    },
    'consumer_analytics_stats': {
        'path': '/api/analytics/consumer-analytics/stats/',
        'method': 'GET',
        'description': 'Estadísticas generales de analítica de consumidores',
        'parameters': {}
    },
    'carbon_footprint_crud': {
        'path': '/api/analytics/carbon-footprint/',
        'method': 'GET, POST, PUT, DELETE',
        'description': 'CRUD completo para huella de carbono',
        'parameters': {
            'animal_id': 'int (opcional)',
            'batch_id': 'int (opcional)',
            'time_range': 'str (opcional)'
        }
    },
    'carbon_footprint_summary': {
        'path': '/api/analytics/carbon-footprint/summary/',
        'method': 'GET',
        'description': 'Resumen de huella de carbono',
        'parameters': {}
    },
    'carbon_footprint_by_animal': {
        'path': '/api/analytics/carbon-footprint/by_animal/',
        'method': 'GET',
        'description': 'Huella de carbono por animal específico',
        'parameters': {
            'animal_id': 'int (requerido)'
        }
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