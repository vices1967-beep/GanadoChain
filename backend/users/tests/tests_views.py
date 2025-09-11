from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import UserActivityLog, UserPreference, APIToken
from users.notification_models import Notification

User = get_user_model()

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
        self.assertIn('email', response.data.get('error', {}).get('details', {}))
    
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
        self.assertIn('wallet_address', response.data.get('error', {}).get('details', {}))
    
    def test_registration_password_mismatch(self):
        """Test para contraseñas que no coinciden"""
        payload = self.valid_payload.copy()
        payload['password2'] = 'DifferentPass123!'
        
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data.get('error', {}).get('details', {}))

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
            wallet_address='0x1111111111111111111111111111111111111111'  # Única
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
            wallet_address='0x2222222222222222222222222222222222222222'  # Única
        )
        
        # Crear admin user
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpass123',
            wallet_address='0x3333333333333333333333333333333333333333',  # Única
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
            wallet_address='0x4444444444444444444444444444444444444444'  # Única
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
            wallet_address='0x5555555555555555555555555555555555555555'  # Única
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