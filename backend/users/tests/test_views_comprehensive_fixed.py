# users/tests/test_views_comprehensive_fixed.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import UserActivityLog, UserPreference, APIToken
from users.notification_models import Notification
from users.reputation_models import UserRole, ReputationScore
from django.utils import timezone
import json

User = get_user_model()

class UserViewSetComprehensiveTestsFixed(APITestCase):
    """Tests corregidos para UserViewSet"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Crear usuario normal
        self.normal_user = User.objects.create_user(
            username='normaluser',
            email='normal@example.com',
            password='testpass123',
            wallet_address='0x2222222222222222222222222222222222222222',
            role='PRODUCER'
        )
        
        # Crear admin user
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpass123',
            wallet_address='0x3333333333333333333333333333333333333333',
            role='ADMIN',
            is_staff=True
        )
        
        # Crear otro usuario para testing
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123',
            wallet_address='0x4444444444444444444444444444444444444444',
            role='VET'
        )
        
        # Configurar clients con tokens
        refresh_normal = RefreshToken.for_user(self.normal_user)
        refresh_admin = RefreshToken.for_user(self.admin_user)
        
        self.normal_client = APIClient()
        self.normal_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh_normal.access_token}')
        
        self.admin_client = APIClient()
        self.admin_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh_admin.access_token}')
        
        # URLs
        self.user_list_url = reverse('users:user-list')
        self.user_detail_url = lambda pk: reverse('users:user-detail', kwargs={'pk': pk})
        self.user_me_url = reverse('users:user-me')
        self.user_update_profile_url = reverse('users:user-update-profile')
        self.user_change_password_url = reverse('users:user-change-password')
        self.user_stats_url = reverse('users:user-stats')
        self.user_search_url = reverse('users:user-search')
    
    def test_user_me_endpoint(self):
        """Test para el endpoint /me"""
        response = self.normal_client.get(self.user_me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'normaluser')
    
    # Tests corregidos para permisos
    def test_user_cannot_access_other_user_detail(self):
        """Test que usuario no puede acceder a detalles de otro usuario"""
        url = self.user_detail_url(self.other_user.id)
        response = self.normal_client.get(url)
        
        # Debería devolver 404 por seguridad
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_user_cannot_update_other_user(self):
        """Test que usuario no puede actualizar otro usuario"""
        url = self.user_detail_url(self.other_user.id)
        update_data = {'first_name': 'Hacked'}
        
        response = self.normal_client.patch(url, update_data, format='json')
        
        # Debería devolver 404 por seguridad
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_user_cannot_delete_other_user(self):
        """Test que usuario no puede eliminar otro usuario"""
        url = self.user_detail_url(self.other_user.id)
        
        response = self.normal_client.delete(url)
        
        # Debería devolver 404 por seguridad
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_admin_can_access_all_users(self):
        """Test que admin puede acceder a todos los usuarios"""
        url = self.user_detail_url(self.normal_user.id)
        response = self.admin_client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'normaluser')
    
    def test_user_stats_admin_only(self):
        """Test que solo admin puede ver estadísticas"""
        # Usuario normal no puede acceder
        response = self.normal_client.get(self.user_stats_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Admin puede acceder
        response = self.admin_client.get(self.user_stats_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_search_admin_only(self):
        """Test que solo admin puede buscar usuarios"""
        data = {'query': 'test'}
        
        # Usuario normal no puede buscar
        response = self.normal_client.get(self.user_search_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Admin puede buscar
        response = self.admin_client.get(self.user_search_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class PasswordResetTestsFixed(APITestCase):
    """Tests corregidos para reset de contraseña"""
    
    def setUp(self):
        self.client = APIClient()
        self.password_reset_url = reverse('users:password-reset')
        self.password_reset_confirm_url = reverse('users:password-reset-confirm')
    
    def test_password_reset_request(self):
        """Test para solicitar reset de contraseña"""
        data = {'email': 'test@example.com'}
        response = self.client.post(self.password_reset_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_password_reset_confirm(self):
        """Test para confirmar reset de contraseña"""
        data = {
            'token': 'test-token-123',
            'new_password': 'NewPass123!',
            'new_password2': 'NewPass123!'
        }
        response = self.client.post(self.password_reset_confirm_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

# Ejecutar solo los tests corregidos