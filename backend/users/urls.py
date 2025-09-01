from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'users'

# Router para ViewSets
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'preferences', views.UserPreferenceViewSet, basename='userpreference')
router.register(r'api-tokens', views.APITokenViewSet, basename='apitoken')
router.register(r'activity-logs', views.UserActivityLogViewSet, basename='useractivitylog')

urlpatterns = [
    # URLs de ViewSets
    path('', include(router.urls)),
    
    # URLs de autenticación JWT
    path('auth/login/', views.UserTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/login/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # URLs de registro y gestión de cuenta
    path('auth/register/', views.UserRegistrationView.as_view(), name='user_registration'),
    path('auth/password/reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('auth/password/reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    # URLs específicas para acciones de usuarios
    path('users/me/', views.UserViewSet.as_view({'get': 'me'}), name='user-me'),
    path('users/me/update-profile/', views.UserViewSet.as_view({'put': 'update_profile'}), name='user-update-profile'),
    path('users/me/change-password/', views.UserViewSet.as_view({'post': 'change_password'}), name='user-change-password'),
    path('users/me/connect-wallet/', views.UserViewSet.as_view({'post': 'connect_wallet'}), name='user-connect-wallet'),
    path('users/me/verify-wallet/', views.UserViewSet.as_view({'post': 'verify_wallet'}), name='user-verify-wallet'),
    path('users/stats/', views.UserViewSet.as_view({'get': 'stats'}), name='user-stats'),
    path('users/search/', views.UserViewSet.as_view({'get': 'search'}), name='user-search'),
    
    # URLs para acciones específicas de tokens API
    path('api-tokens/<int:pk>/regenerate/', views.APITokenViewSet.as_view({'post': 'regenerate'}), name='api-token-regenerate'),
    
    # URLs para actividad de usuarios
    path('activity-logs/recent/', views.UserActivityLogViewSet.as_view({'get': 'recent'}), name='activity-logs-recent'),
    
    # URLs de compatibilidad (mantenidas para versiones anteriores)
    path('profile/', views.UserProfileView.as_view(), name='user_profile_legacy'),
]

# URLs para API docs y exploración
urlpatterns += [
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]