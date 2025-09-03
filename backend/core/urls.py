"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Importar vistas de core
from . import views

# Configuración de Swagger/OpenAPI
schema_view = get_schema_view(
    openapi.Info(
        title="GanadoChain API",
        default_version='v1',
        description="API Documentation for GanadoChain - Blockchain Cattle Tracking System",
        terms_of_service="https://ganadochain.com/terms/",
        contact=openapi.Contact(email="support@ganadochain.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

def home(request):
    return JsonResponse({
        'message': '🐄 Bienvenido a GanadoChain API',
        'version': '1.0.0',
        'description': 'Sistema de Trazabilidad Blockchain para Ganado',
        'documentation': {
            'swagger': '/swagger/',
            'redoc': '/redoc/',
            'api_root': '/api/'
        },
        'endpoints': {
            'core': {
                'health': '/api/core/health/',
                'info': '/api/core/info/',
                'config': '/api/core/config/',
                'metrics': '/api/core/metrics/',
                'dashboard': '/api/core/dashboard/stats/'
            },
            'auth': {
                'login': '/api/auth/login/',
                'register': '/api/auth/register/',
                'refresh': '/api/auth/login/refresh/'
            },
            'cattle': {
                'animals': '/api/cattle/animals/',
                'batches': '/api/cattle/batches/',
                'health_records': '/api/cattle/health-records/'
            },
            'iot': {
                'devices': '/api/iot/devices/',
                'gps_data': '/api/iot/gps-data/',
                'health_data': '/api/iot/health-data/'
            },
            'blockchain': {
                'events': '/api/blockchain/events/',
                'transactions': '/api/blockchain/contract-interactions/',
                'nft_mint': '/api/blockchain/mint-nft/'
            },
            'users': {
                'profile': '/api/users/users/me/',
                'preferences': '/api/users/preferences/'
            }
        },
        'status': 'operational',
        'blockchain_network': 'Polygon Amoy Testnet',
        'support': {
            'email': 'support@ganadochain.com',
            'documentation': 'https://docs.ganadochain.com'
        }
    })

urlpatterns = [
    # Home page
    path('', home, name='home'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # Core API Routes (NUEVAS)
    path('api/core/', include([
        # Health check e información
        path('health/', views.HealthCheckView.as_view(), name='health-check'),
        path('info/', views.APIInfoView.as_view(), name='api-info'),
        path('config/', views.SystemConfigView.as_view(), name='system-config'),
        
        # Dashboard y estadísticas
        path('dashboard/stats/', views.DashboardStatsView.as_view(), name='dashboard-stats'),
        
        # Métricas del sistema
        path('metrics/', include([
            path('', views.SystemMetricsViewSet.as_view({'get': 'list'}), name='metrics-list'),
            path('latest/', views.SystemMetricsViewSet.as_view({'get': 'latest'}), name='metrics-latest'),
            path('summary/', views.SystemMetricsViewSet.as_view({'get': 'summary'}), name='metrics-summary'),
        ])),
        
        # Mantenimiento y utilidades
        path('maintenance/', views.SystemMaintenanceView.as_view(), name='system-maintenance'),
        path('validate/', views.ValidationTestView.as_view(), name='validation-test'),
        path('error-test/', views.ErrorTestView.as_view(), name='error-test'),
    ])),
    
    # API Routes de las apps
    path('api/auth/', include('users.urls')),
    path('api/cattle/', include('cattle.urls')),
    path('api/iot/', include('iot.urls')),
    path('api/blockchain/', include('blockchain.urls')),
    path('api/users/', include('users.urls')),
    
    # Health check endpoint legacy (mantener por compatibilidad)
    path('health/', lambda request: JsonResponse({'status': 'healthy'}), name='legacy-health-check'),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Handler para errores 404
handler404 = lambda request, exception: JsonResponse({
    'error': 'Endpoint no encontrado',
    'message': 'El endpoint solicitado no existe',
    'documentation': '/swagger/',
    'available_endpoints': {
        'core': '/api/core/',
        'auth': '/api/auth/',
        'cattle': '/api/cattle/',
        'iot': '/api/iot/',
        'blockchain': '/api/blockchain/',
        'users': '/api/users/'
    }
}, status=404)

# Handler para errores 500
handler500 = lambda request: JsonResponse({
    'error': 'Error interno del servidor',
    'message': 'Ha ocurrido un error inesperado',
    'support': 'support@ganadochain.com',
    'incident_id': f'ERR_{int(datetime.now().timestamp())}'
}, status=500)