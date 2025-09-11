# users/tests/test_views_missing_coverage.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import UserActivityLog, APIToken
from users.notification_models import Notification
from users.reputation_models import UserRole, ReputationScore
from django.utils import timezone

User = get_user_model()

class MissingCoverageTests(APITestCase):
    """Tests para cubrir las líneas faltantes en views.py"""
    
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
        
        # Configurar clients con tokens
        refresh_normal = RefreshToken.for_user(self.normal_user)
        refresh_admin = RefreshToken.for_user(self.admin_user)
        
        self.normal_client = APIClient()
        self.normal_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh_normal.access_token}')
        
        self.admin_client = APIClient()
        self.admin_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh_admin.access_token}')
    
    def test_connect_wallet_success(self):
        """Test para conectar wallet exitosamente"""
        url = reverse('users:user-connect-wallet', kwargs={'pk': self.normal_user.id})
        data = {
            'wallet_address': '0x1234567890abcdef1234567890abcdef12345678',
            'signature': '0x' + 'a' * 130,
            'message': 'Test message'
        }
        
        response = self.normal_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_connect_wallet_duplicate(self):
        """Test para conectar wallet con dirección duplicada"""
        # Primero crear otro usuario con la wallet
        other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='testpass123',
            wallet_address='0x1234567890abcdef1234567890abcdef12345678'
        )
        
        url = reverse('users:user-connect-wallet', kwargs={'pk': self.normal_user.id})
        data = {
            'wallet_address': '0x1234567890abcdef1234567890abcdef12345678',
            'signature': '0x' + 'a' * 130,
            'message': 'Test message'
        }
        
        response = self.normal_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_verify_wallet_success(self):
        """Test para verificar wallet exitosamente"""
        # Primero asignar wallet
        self.normal_user.wallet_address = '0x1234567890abcdef1234567890abcdef12345678'
        self.normal_user.save()
        
        url = reverse('users:user-verify-wallet', kwargs={'pk': self.normal_user.id})
        data = {
            'wallet_address': '0x1234567890abcdef1234567890abcdef12345678',
            'signed_message': '0x' + 'b' * 130,
            'original_message': 'Verify'
        }
        
        response = self.normal_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_stats_admin_access(self):
        """Test que admin puede ver stats"""
        url = reverse('users:user-stats')
        response = self.admin_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_users', response.data)
    
    def test_user_search_functionality(self):
        """Test de búsqueda de usuarios"""
        url = reverse('users:user-search')
        data = {'query': 'normal', 'search_in': ['username']}
        
        response = self.admin_client.get(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_user_notifications_access(self):
        """Test para acceder a notificaciones"""
        # Crear notificación
        Notification.objects.create(
            user=self.normal_user,
            notification_type='HEALTH_ALERT',
            title='Test',
            message='Test message'
        )
        
        url = reverse('users:user-notifications', kwargs={'pk': self.normal_user.id})
        response = self.normal_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_roles_access(self):
        """Test para acceder a roles"""
        # Crear rol
        UserRole.objects.create(
            user=self.normal_user,
            role_type='PRODUCER_ROLE',
            scope_type='GLOBAL'
        )
        
        url = reverse('users:user-roles', kwargs={'pk': self.normal_user.id})
        response = self.normal_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_reputation_access(self):
        """Test para acceder a reputación"""
        # Crear reputación
        ReputationScore.objects.create(
            user=self.normal_user,
            reputation_type='PRODUCER',
            score=4.5
        )
        
        url = reverse('users:user-reputation', kwargs={'pk': self.normal_user.id})
        response = self.normal_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_client_ip_method(self):
        """Test para el método get_client_ip"""
        # Este método es usado internamente, necesitamos probarlo indirectamente
        # a través de una acción que lo use, como change_password
        
        data = {
            'old_password': 'testpass123',
            'new_password': 'NewPass123!',
            'new_password2': 'NewPass123!'
        }
        
        url = reverse('users:user-change-password')
        response = self.normal_client.post(url, data, format='json')
        
        # Verificar que se creó un activity log con IP
        log = UserActivityLog.objects.filter(
            user=self.normal_user,
            action='PASSWORD_CHANGE'
        ).first()
        
        self.assertIsNotNone(log)
        self.assertIsNotNone(log.ip_address)

class ErrorHandlingTests(APITestCase):
    """Tests para manejo de errores"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            wallet_address='0x1111111111111111111111111111111111111111'
        )
        
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_permission_denied_handling(self):
        """Test para manejo de PermissionDenied"""
        # Intentar acceder a endpoint de admin sin permisos
        url = reverse('users:user-stats')
        response = self.client.get(url)
        
        # Debería devolver 403
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)