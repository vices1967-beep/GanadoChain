import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import UserActivityLog, UserPreference, APIToken
from .notification_models import Notification
from users.reputation_models import UserRole, ReputationScore
import tempfile
from PIL import Image

User = get_user_model()

class UserModelTests(APITestCase):
    """Tests para el modelo User"""
    
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'wallet_address': '0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
            'role': 'PRODUCER'
        }
        self.user = User.objects.create_user(**self.user_data)
    
    def test_user_creation(self):
        """Test para crear un usuario"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.role, 'PRODUCER')
        self.assertTrue(self.user.check_password('testpass123'))
    
    def test_wallet_address_normalization(self):
        """Test para normalización de dirección wallet"""
        user = User.objects.create_user(
            username='test2',
            email='test2@example.com',
            password='testpass123',
            wallet_address='742d35cc6634c0532925a3b844bc454e4438f44f'  # Sin 0x
        )
        self.assertEqual(user.wallet_address, '0x742d35cc6634c0532925a3b844bc454e4438f44f')
    
    def test_user_str_representation(self):
        """Test para representación string del usuario"""
        expected_str = f"{self.user.username} - {self.user.get_role_display()} ({self.user.wallet_short})"
        self.assertEqual(str(self.user), expected_str)
    
    def test_profile_completion_calculation(self):
        """Test para cálculo de completitud de perfil"""
        # Usuario con pocos campos completados
        self.assertLess(self.user.profile_completion, 50)
        
        # Completar más campos
        self.user.phone_number = '+1234567890'
        self.user.company = 'Test Company'
        self.user.location = 'Test Location'
        self.user.save()
        
        self.assertGreater(self.user.profile_completion, 50)
    
    def test_role_properties(self):
        """Test para propiedades de roles"""
        self.assertTrue(self.user.is_producer)
        self.assertFalse(self.user.is_veterinarian)
        
        # Añadir rol de veterinario en blockchain
        self.user.blockchain_roles = ['VET_ROLE']
        self.user.save()
        self.assertTrue(self.user.is_veterinarian)

class UserRegistrationTests(APITestCase):
    """Tests para registro de usuarios"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('users:user-register')
        self.valid_payload = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'first_name': 'New',
            'last_name': 'User',
            'wallet_address': '0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
            'role': 'PRODUCER'
        }
    
    def test_valid_registration(self):
        """Test para registro válido"""
        response = self.client.post(self.register_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'newuser')
    
    def test_registration_with_existing_email(self):
        """Test para registro con email existente"""
        User.objects.create_user(
            username='existing',
            email='newuser@example.com',
            password='testpass123',
            wallet_address='0x1234567890abcdef1234567890abcdef12345678'
        )
        
        response = self.client.post(self.register_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)  # En lugar de response.data.get('error', {}).get('details', {})
    
    def test_registration_with_existing_wallet(self):
        """Test para registro con wallet existente"""
        User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='testpass123',
            wallet_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        )
        
        response = self.client.post(self.register_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Verificar la nueva estructura de respuesta
        error_details = response.data.get('error', {}).get('details', {})
        self.assertIn('wallet_address', response.data)  # En lugar de error_details
    
    def test_registration_password_mismatch(self):
        """Test para contraseñas que no coinciden"""
        payload = self.valid_payload.copy()
        payload['password2'] = 'DifferentPass123!'
        
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
        self.assertEqual(response.data['password'][0], 'Las contraseñas no coinciden.')

class UserAuthenticationTests(APITestCase):
    """Tests para autenticación de usuarios"""
    
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('users:token-obtain-pair')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            wallet_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        )
    
    def test_valid_login(self):
        """Test para login válido"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_invalid_login(self):
        """Test para login inválido"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_token_refresh(self):
        """Test para refresh de token"""
        # Primero obtener tokens
        login_response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        }, format='json')
        
        refresh_token = login_response.data['refresh']
        refresh_url = reverse('users:token-refresh')
        
        response = self.client.post(refresh_url, {
            'refresh': refresh_token
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

class UserProfileTests(APITestCase):
    """Tests para perfiles de usuario"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            wallet_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        )
        
        # Obtener token JWT
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        self.profile_url = reverse('users:user-me')
        self.update_url = reverse('users:user-update-profile')
    
    def test_get_user_profile(self):
        """Test para obtener perfil de usuario"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')
    
    def test_update_user_profile(self):
        """Test para actualizar perfil de usuario"""
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '+1234567890',
            'company': 'Test Company',
            'location': 'Test Location'
        }
        
        response = self.client.put(self.update_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que los datos se actualizaron
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.phone_number, '+1234567890')
    
    def test_change_password(self):
        """Test para cambiar contraseña"""
        change_password_url = reverse('users:user-change-password')
        data = {
            'old_password': 'testpass123',
            'new_password': 'NewComplexPass123!',
            'new_password2': 'NewComplexPass123!'
        }
        
        response = self.client.post(change_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que la contraseña cambió
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewComplexPass123!'))
    
    def test_change_password_wrong_old_password(self):
        """Test para cambiar contraseña con contraseña antigua incorrecta"""
        change_password_url = reverse('users:user-change-password')
        data = {
            'old_password': 'wrongpassword',
            'new_password': 'NewComplexPass123!',
            'new_password2': 'NewComplexPass123!'
        }
        
        response = self.client.post(change_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class UserPermissionTests(APITestCase):
    """Tests para permisos de usuario"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Crear usuario normal
        self.normal_user = User.objects.create_user(
            username='normaluser',
            email='normal@example.com',
            password='testpass123',
            wallet_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        )
        
        # Crear admin user
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpass123',
            wallet_address='0x1234567890abcdef1234567890abcdef12345678',
            is_staff=True
        )
        
        # Obtener tokens
        refresh_normal = RefreshToken.for_user(self.normal_user)
        refresh_admin = RefreshToken.for_user(self.admin_user)
        
        self.normal_client = APIClient()
        self.normal_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh_normal.access_token}')
        
        self.admin_client = APIClient()
        self.admin_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh_admin.access_token}')
    
    def test_normal_user_cannot_access_other_profiles(self):
        """Test que usuario normal no puede acceder a otros perfiles"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123',
            wallet_address='0x1111111111111111111111111111111111111111'
        )
        
        url = reverse('users:user-detail', kwargs={'pk': other_user.id})
        response = self.normal_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_admin_can_access_all_profiles(self):
        """Test que admin puede acceder a todos los perfiles"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123',
            wallet_address='0x1111111111111111111111111111111111111111'
        )
        
        url = reverse('users:user-detail', kwargs={'pk': other_user.id})
        response = self.admin_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_stats_permissions(self):
        """Test para permisos de estadísticas de usuarios"""
        stats_url = reverse('users:user-stats')
        
        # Usuario normal no puede acceder
        response = self.normal_client.get(stats_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Admin puede acceder
        response = self.admin_client.get(stats_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class UserActivityLogTests(APITestCase):
    """Tests para registros de actividad de usuario"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            wallet_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        )
        
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Crear algunos registros de actividad
        UserActivityLog.objects.create(
            user=self.user,
            action='LOGIN',
            ip_address='127.0.0.1'
        )
        UserActivityLog.objects.create(
            user=self.user,
            action='PROFILE_UPDATE',
            ip_address='127.0.0.1'
        )
    
    def test_get_activity_logs(self):
        """Test para obtener registros de actividad"""
        url = reverse('users:useractivitylog-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_recent_activity(self):
        """Test para actividad reciente"""
        url = reverse('users:useractivitylog-recent')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

class UserPreferenceTests(APITestCase):
    """Tests para preferencias de usuario"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            wallet_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        )
        
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Crear preferencias por defecto
        UserPreference.objects.create(user=self.user)
    
    def test_get_user_preferences(self):
        """Test para obtener preferencias de usuario"""
        url = reverse('users:userpreference-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['results'][0]['email_notifications'])
    
    def test_update_user_preferences(self):
        """Test para actualizar preferencias de usuario"""
        url = reverse('users:userpreference-detail', kwargs={'pk': self.user.preferences.id})
        update_data = {
            'email_notifications': False,
            'language': 'en',
            'theme': 'dark'
        }
        
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que se actualizaron
        self.user.preferences.refresh_from_db()
        self.assertFalse(self.user.preferences.email_notifications)
        self.assertEqual(self.user.preferences.language, 'en')

class APITokenTests(APITestCase):
    """Tests para tokens de API"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            wallet_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        )
        
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_create_api_token(self):
        """Test para crear token de API"""
        url = reverse('users:apitoken-list')
        data = {
            'name': 'Test Token',
            'token_type': 'READ',
            'expires_at': (timezone.now() + timezone.timedelta(days=30)).isoformat()
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(APIToken.objects.count(), 1)
    
    def test_list_api_tokens(self):
        """Test para listar tokens de API"""
        # Crear un token primero
        APIToken.objects.create(
            user=self.user,
            name='Test Token',
            token='testtoken123',
            token_type='READ'
        )
        
        url = reverse('users:apitoken-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

class NotificationTests(APITestCase):
    """Tests para notificaciones"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            wallet_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        )
        
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Crear algunas notificaciones
        Notification.objects.create(
            user=self.user,
            notification_type='HEALTH_ALERT',
            title='Test Notification',
            message='This is a test notification'
        )
    
    def test_get_notifications(self):
        """Test para obtener notificaciones"""
        url = reverse('users:notification-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_mark_notification_as_read(self):
        """Test para marcar notificación como leída"""
        notification = Notification.objects.first()
        url = reverse('users:notification-mark-read', kwargs={'pk': notification.id})
        
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

class WalletConnectTests(APITestCase):
    """Tests para conexión de wallet"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            wallet_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        )
        
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_wallet_connect(self):
        """Test para conectar wallet"""
        url = reverse('users:wallet-connect')
        data = {
            'wallet_address': '0x1234567890abcdef1234567890abcdef12345678'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.wallet_address, '0x1234567890abcdef1234567890abcdef12345678')
    
    def test_wallet_connect_invalid_address(self):
        """Test para conectar wallet con dirección inválida"""
        url = reverse('users:wallet-connect')
        data = {
            'wallet_address': 'invalid-address'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class UserSearchTests(APITestCase):
    """Tests para búsqueda de usuarios"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Crear admin user para búsquedas
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpass123',
            wallet_address='0x1234567890abcdef1234567890abcdef12345678',
            is_staff=True
        )
        
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Crear usuarios de prueba
        User.objects.create_user(
            username='john_doe',
            email='john@example.com',
            password='testpass123',
            wallet_address='0x1111111111111111111111111111111111111111',
            first_name='John',
            last_name='Doe',
            company='ABC Corp'
        )
        
        User.objects.create_user(
            username='jane_smith',
            email='jane@example.com',
            password='testpass123',
            wallet_address='0x2222222222222222222222222222222222222222',
            first_name='Jane',
            last_name='Smith',
            company='XYZ Inc'
        )
    
    def test_search_users_by_username(self):
        """Test para buscar usuarios por username"""
        url = reverse('users:user-search')
        response = self.client.get(f"{url}?query=john&search_in=username")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'john_doe')
    
    def test_search_users_by_email(self):
        """Test para buscar usuarios por email"""
        url = reverse('users:user-search')
        response = self.client.get(f"{url}?query=@example.com&search_in=email")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # Debería encontrar ambos usuarios
    
    def test_search_users_by_company(self):
        """Test para buscar usuarios por empresa"""
        url = reverse('users:user-search')
        response = self.client.get(f"{url}?query=XYZ&search_in=company")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['company'], 'XYZ Inc')

class UserStatsTests(APITestCase):
    """Tests para estadísticas de usuarios"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Crear admin user
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpass123',
            wallet_address='0x1234567890abcdef1234567890abcdef12345678',
            is_staff=True
        )
        
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Crear algunos usuarios para estadísticas
        for i in range(5):
            User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password='testpass123',
                wallet_address=f'0x{i:040x}',
                role='PRODUCER' if i % 2 == 0 else 'VET'
            )
    
    def test_user_stats(self):
        """Test para obtener estadísticas de usuarios"""
        url = reverse('users:user-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_users'], 6)  # 5 creados + admin
        self.assertIn('users_by_role', response.data)
        self.assertGreater(response.data['users_by_role']['PRODUCER'], 0)

class UserRoleTests(APITestCase):
    """Tests para roles de usuario"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            wallet_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        )
        
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Crear algunos roles
        UserRole.objects.create(
            user=self.user,
            role_type='PRODUCER_ROLE',
            scope_type='GLOBAL'
        )
    
    def test_get_user_roles(self):
        """Test para obtener roles de usuario"""
        url = reverse('users:userrole-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['role_type'], 'PRODUCER_ROLE')

class ReputationScoreTests(APITestCase):
    """Tests para puntuaciones de reputación"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            wallet_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        )
        
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Crear puntuación de reputación
        ReputationScore.objects.create(
            user=self.user,
            reputation_type='PRODUCER',
            score=85.5,
            total_actions=100,
            positive_actions=85
        )
    
    def test_get_reputation_scores(self):
        """Test para obtener puntuaciones de reputación"""
        url = reverse('users:reputationscore-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['score'], '85.50')