from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'blockchain'

router = DefaultRouter()
router.register(r'events', views.BlockchainEventViewSet, basename='blockchainevent')
router.register(r'contract-interactions', views.ContractInteractionViewSet, basename='contractinteraction')
router.register(r'smart-contracts', views.SmartContractViewSet, basename='smartcontract')

urlpatterns = [
    path('', include(router.urls)),
    path('assign-role/', views.AssignRoleView.as_view(), name='assign-role'),
    path('mint-nft/', views.MintNFTView.as_view(), name='mint-nft'),
    path('check-role/', views.CheckRoleView.as_view(), name='check-role'),
    path('mint-tokens/', views.MintTokensView.as_view(), name='mint-tokens'),
    path('update-health/', views.UpdateHealthView.as_view(), name='update-health'),
    path('iot-health-data/', views.IoTHealthDataView.as_view(), name='iot-health-data'),
    path('animal-history/<int:animal_id>/', views.AnimalHistoryView.as_view(), name='animal-history'),
    path('network-status/', views.NetworkStatusView.as_view(), name='network-status'),
    path('transaction-status/<str:tx_hash>/', views.TransactionStatusView.as_view(), name='transaction-status'),
    path('gas-price/', views.GasPriceView.as_view(), name='gas-price'),
    path('stats/', views.BlockchainStatsView.as_view(), name='blockchain-stats'),
    path('create-batch/', views.BatchCreateView.as_view(), name='create-batch'),
]