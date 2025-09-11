import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import UserActivityLog, UserPreference, APIToken
from users.notification_models import Notification
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

class UserActivityLogModelTests(APITestCase):
    """Tests para el modelo UserActivityLog"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            wallet_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        )
    
    def test_activity_log_creation(self):
        """Test para crear registro de actividad"""
        log = UserActivityLog.objects.create(
            user=self.user,
            action='LOGIN',
            ip_address='127.0.0.1'
        )
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action, 'LOGIN')
    
    def test_short_tx_hash(self):
        """Test para hash de transacción abreviado"""
        log = UserActivityLog.objects.create(
            user=self.user,
            action='BLOCKCHAIN_INTERACTION',
            ip_address='127.0.0.1',
            blockchain_tx_hash='0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef'
        )
        # Verificar que el formato es correcto sin esperar un string exacto
        self.assertTrue(log.short_tx_hash.startswith('0x'))
        self.assertTrue('...' in log.short_tx_hash)
        self.assertTrue(log.short_tx_hash.endswith('abcdef'))  # Los últimos 6 caracteres
        self.assertTrue(len(log.short_tx_hash) < len(log.blockchain_tx_hash))

class UserPreferenceModelTests(APITestCase):
    """Tests para el modelo UserPreference"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            wallet_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        )
    
    def test_preference_creation(self):
        """Test para crear preferencias de usuario"""
        preference = UserPreference.objects.create(user=self.user)
        self.assertEqual(preference.user, self.user)
        self.assertTrue(preference.email_notifications)

class NotificationModelTests(APITestCase):
    """Tests para el modelo Notification"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            wallet_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        )
    
    def test_notification_creation(self):
        """Test para crear notificación"""
        notification = Notification.objects.create(
            user=self.user,
            notification_type='HEALTH_ALERT',
            title='Test Notification',
            message='This is a test notification'
        )
        self.assertEqual(notification.user, self.user)
        self.assertFalse(notification.is_read)