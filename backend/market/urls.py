from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MarketListingViewSet, 
    TradeViewSet, 
    MarketStatsView, 
    PriceHistoryView,
    ExecuteTradeView,
    AnimalMarketView
)

router = DefaultRouter()
router.register(r'listings', MarketListingViewSet, basename='marketlisting')
router.register(r'trades', TradeViewSet, basename='trade')

urlpatterns = [
    # -------------------------------------------------------------------------
    # RUTAS DEL ROUTER (API REST)
    # -------------------------------------------------------------------------
    path('', include(router.urls)),
    
    # -------------------------------------------------------------------------
    # ESTADÍSTICAS DEL MERCADO
    # -------------------------------------------------------------------------
    path(
        'stats/', 
        MarketStatsView.as_view(), 
        name='market-stats',
        kwargs={'description': 'Estadísticas generales del mercado'}
    ),
    
    # -------------------------------------------------------------------------
    # HISTORIAL DE PRECIOS
    # -------------------------------------------------------------------------
    path(
        'price-history/', 
        PriceHistoryView.as_view(), 
        name='price-history',
        kwargs={'description': 'Historial de precios general del mercado'}
    ),
    path(
        'price-history/<int:animal_id>/', 
        PriceHistoryView.as_view(), 
        name='animal-price-history',
        kwargs={'description': 'Historial de precios de un animal específico'}
    ),
    
    # -------------------------------------------------------------------------
    # EJECUCIÓN DE TRADES
    # -------------------------------------------------------------------------
    path(
        'execute-trade/<int:listing_id>/', 
        ExecuteTradeView.as_view(), 
        name='execute-trade',
        kwargs={'description': 'Ejecutar una compra en el mercado'}
    ),
    
    # -------------------------------------------------------------------------
    # VISTA DE MERCADO POR ANIMAL
    # -------------------------------------------------------------------------
    path(
        'animal/<int:animal_id>/', 
        AnimalMarketView.as_view(), 
        name='animal-market',
        kwargs={'description': 'Información completa de mercado para un animal'}
    ),
    
    # -------------------------------------------------------------------------
    # ENDPOINTS ESPECÍFICOS PARA ACCIONES PERSONALIZADAS
    # -------------------------------------------------------------------------
    path(
        'listings/<int:pk>/cancel/', 
        MarketListingViewSet.as_view({'post': 'cancel_listing'}), 
        name='cancel-listing',
        kwargs={'description': 'Cancelar un listado activo'}
    ),
    path(
        'my/listings/', 
        MarketListingViewSet.as_view({'get': 'my_listings'}), 
        name='my-listings',
        kwargs={'description': 'Obtener todos los listados del usuario actual'}
    ),
    path(
        'my/trades/', 
        TradeViewSet.as_view({'get': 'my_trades'}), 
        name='my-trades',
        kwargs={'description': 'Obtener todos los trades del usuario actual'}
    ),
]

# Para incluir en el urls.py principal
app_name = 'market'

# Documentación de parámetros de query disponibles
MARKET_QUERY_PARAMS = {
    'listings': {
        'animal_id': 'Filtrar por ID de animal',
        'seller_id': 'Filtrar por ID de vendedor',
        'min_price': 'Precio mínimo',
        'max_price': 'Precio máximo',
        'currency': 'Filtrar por moneda (USDC, DAI, etc.)',
        'breed': 'Filtrar por raza del animal'
    },
    'trades': {
        'listing_id': 'Filtrar por ID de listado',
        'buyer_id': 'Filtrar por ID de comprador',
        'status': 'Filtrar por estado del trade'
    },
    'price-history': {
        'days': 'Número de días para el historial (default: 30)'
    }
}

# Ejemplos de uso para documentación
MARKET_API_EXAMPLES = {
    'listings': {
        'all_active': '/market/listings/',
        'filtered': '/market/listings/?min_price=100&currency=USDC&breed=Angus',
        'user_listings': '/market/my/listings/'
    },
    'trades': {
        'all': '/market/trades/',
        'user_trades': '/market/my/trades/',
        'filtered': '/market/trades/?status=COMPLETED&buyer_id=123'
    },
    'stats': {
        'general': '/market/stats/'
    },
    'price_history': {
        'general': '/market/price-history/',
        'specific_animal': '/market/price-history/456/'
    },
    'trading': {
        'execute': '/market/execute-trade/789/',
        'cancel': '/market/listings/789/cancel/'
    },
    'animal_market': {
        'details': '/market/animal/456/'
    }
}