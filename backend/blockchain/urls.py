from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'blockchain'

router = DefaultRouter()
router.register(r'events', views.BlockchainEventViewSet, basename='blockchainevent')
router.register(r'interactions', views.ContractInteractionViewSet, basename='contractinteraction')
router.register(r'contracts', views.SmartContractViewSet, basename='smartcontract')
router.register(r'network-state', views.NetworkStateViewSet, basename='networkstate')
router.register(r'gas-price-history', views.GasPriceHistoryViewSet, basename='gaspricehistory')
router.register(r'transaction-pool', views.TransactionPoolViewSet, basename='transactionpool')

urlpatterns = [
    # Operaciones con contratos
    path('mint/nft/', views.MintNFTView.as_view(), name='mint-nft'),
    path('mint/tokens/', views.MintTokensView.as_view(), name='mint-tokens'),
    path('assign-role/', views.AssignRoleView.as_view(), name='assign-role'),
    path('check-role/', views.CheckRoleView.as_view(), name='check-role'),
    path('update-health/', views.UpdateHealthView.as_view(), name='update-health'),
    path('create-batch/', views.BatchCreateView.as_view(), name='create-batch'),
    path('call-contract/', views.ContractCallView.as_view(), name='call-contract'),
    path('subscribe-event/', views.EventSubscriptionView.as_view(), name='subscribe-event'),
    
    # Datos IoT
    path('iot/health-data/', views.IoTHealthDataView.as_view(), name='iot-health-data'),
    
    # Consultas y estado
    path('network/status/', views.NetworkStatusView.as_view(), name='network-status'),
    path('transaction/<str:tx_hash>/status/', views.TransactionStatusView.as_view(), name='transaction-status'),
    path('gas-price/', views.GasPriceView.as_view(), name='gas-price'),
    path('stats/', views.BlockchainStatsView.as_view(), name='blockchain-stats'),
    path('animal/<int:animal_id>/history/', views.AnimalHistoryView.as_view(), name='animal-history'),
    
    # Nuevas URLs para compatibilidad con tests
    path('api/balance/', views.GetBalanceView.as_view(), name='get-balance'),
    path('api/token/balance/', views.GetTokenBalanceView.as_view(), name='token-balance'),
    path('api/nft/animal/<int:animal_id>/', views.GetAnimalNFTInfoView.as_view(), name='animal-nft-info'),
    path('api/nft/verify/<int:animal_id>/', views.VerifyAnimalNFTView.as_view(), name='verify-animal-nft'),
    
    # Incluir rutas del router
    path('', include(router.urls)),
]