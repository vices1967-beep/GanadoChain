from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from blockchain.views import AssignRoleView, CheckRoleView

app_name = 'users'

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'preferences', views.UserPreferenceViewSet, basename='userpreference')
router.register(r'api-tokens', views.APITokenViewSet, basename='apitoken')
router.register(r'activity-logs', views.UserActivityLogViewSet, basename='useractivitylog')
router.register(r'notifications', views.NotificationViewSet, basename='notification')
router.register(r'user-roles', views.UserRoleViewSet, basename='userrole')
router.register(r'reputation-scores', views.ReputationScoreViewSet, basename='reputationscore')

urlpatterns = [
    # Autenticación
    path('auth/register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('auth/login/', views.UserTokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/password/reset/', views.PasswordResetView.as_view(), name='password-reset'),
    path('auth/password/reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    
    # Perfil de usuario
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    
    # Wallet y blockchain
    path('wallet/connect/', views.WalletConnectView.as_view(), name='wallet-connect'),
    #path('wallet/verify/', views.VerifyWalletView.as_view(), name='wallet-verify'),
    path('roles/assign/', AssignRoleView.as_view(), name='assign-role'),
    path('roles/check/', CheckRoleView.as_view(), name='check-role'),
    
    # Búsqueda y utilidades
    #path('search/', views.UserSearchView.as_view(), name='user-search'),
    #spath('stats/', views.UserStatsView.as_view(), name='user-stats'),
    #path('export/', views.UserExportView.as_view(), name='user-export'),
    
    # Incluir rutas del router
    path('', include(router.urls)),
]