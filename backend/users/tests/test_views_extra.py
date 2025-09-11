from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import UserActivityLog, UserPreference, APIToken
from users.notification_models import Notification
from django.utils import timezone  # Añadir esto al inicio
User = get_user_model()

class UserActivityLogTests(APITestCase):
    """Tests para registros de actividad de usuario"""
    
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
            wallet_address='0x2222222222222222222222222222222222222222'
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
            wallet_address='0x3333333333333333333333333333333333333333'
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
            wallet_address='0x4444444444444444444444444444444444444444'
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
            wallet_address='0x5555555555555555555555555555555555555555'
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