from django.urls import path
from .advanced_views import SmartContractAdminView, EventSubscriptionView, GasOptimizationView, CrossChainView

urlpatterns = [
    path('contracts/admin/', SmartContractAdminView.as_view({'get': 'list', 'post': 'create'}), name='contract-admin'),
    path('contracts/admin/<int:pk>/', SmartContractAdminView.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='contract-admin-detail'),
    path('contracts/admin/<int:pk>/upgrade/', SmartContractAdminView.as_view({'post': 'upgrade'}), name='contract-upgrade'),
    path('events/subscribe/', EventSubscriptionView.as_view(), name='event-subscribe'),
    path('gas/optimize/', GasOptimizationView.as_view(), name='gas-optimize'),
    path('cross-chain/', CrossChainView.as_view(), name='cross-chain'),
]
