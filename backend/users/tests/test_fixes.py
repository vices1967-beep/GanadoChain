# users/tests/test_fixes.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class PermissionFixTests(APITestCase):
    """Tests para corregir las assertions de permisos"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.normal_user = User.objects.create_user(
            username='normaluser',
            email='normal@example.com',
            password='testpass123',
            wallet_address='0x2222222222222222222222222222222222222222'
        )
        
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123',
            wallet_address='0x3333333333333333333333333333333333333333'
        )
        
        refresh = RefreshToken.for_user(self.normal_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_user_cannot_access_other_user_fixed(self):
        """Test corregido para acceso a otros usuarios"""
        url = reverse('users:user-detail', kwargs={'pk': self.other_user.id})
        response = self.client.get(url)
        
        # DRF puede devolver 403 o 404 - ambos son válidos
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])
    
    def test_user_cannot_update_other_user_fixed(self):
        """Test corregido para actualizar otros usuarios"""
        url = reverse('users:user-detail', kwargs={'pk': self.other_user.id})
        response = self.client.patch(url, {'first_name': 'test'})
        
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])
    
    def test_user_cannot_delete_other_user_fixed(self):
        """Test corregido para eliminar otros usuarios"""
        url = reverse('users:user-detail', kwargs={'pk': self.other_user.id})
        response = self.client.delete(url)
        
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

class WalletValidationFixTests(APITestCase):
    """Tests para validación corregida de wallets"""
    
    def test_wallet_validation_in_registration(self):
        """Test que la validación de wallet funciona en registro"""
        from users.serializers import UserRegistrationSerializer
        
        invalid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
            'wallet_address': 'invalid-address',
            'role': 'PRODUCER'
        }
        
        serializer = UserRegistrationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('wallet_address', serializer.errors)
    
    def test_wallet_validation_in_connect(self):
        """Test que la validación de wallet funciona en conexión"""
        from users.serializers import WalletConnectSerializer
        
        invalid_data = {
            'wallet_address': 'invalid-address',
            'signature': '0x' + 'a' * 130,
            'message': 'test'
        }
        
        serializer = WalletConnectSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('wallet_address', serializer.errors)