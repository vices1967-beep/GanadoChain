# users/tests/test_views_comprehensive.py
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

class UserViewSetComprehensiveTests(APITestCase):
    """Tests completos para UserViewSet cubriendo todas las funcionalidades"""
    
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
        refresh_other = RefreshToken.for_user(self.other_user)
        
        self.normal_client = APIClient()
        self.normal_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh_normal.access_token}')
        
        self.admin_client = APIClient()
        self.admin_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh_admin.access_token}')
        
        self.other_client = APIClient()
        self.other_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh_other.access_token}')
        
        # URLs
        self.user_list_url = reverse('users:user-list')
        self.user_detail_url = lambda pk: reverse('users:user-detail', kwargs={'pk': pk})
        self.user_me_url = reverse('users:user-me')
        self.user_update_profile_url = reverse('users:user-update-profile')
        self.user_change_password_url = reverse('users:user-change-password')
        self.user_connect_wallet_url = lambda pk: reverse('users:user-connect-wallet', kwargs={'pk': pk})
        self.user_verify_wallet_url = lambda pk: reverse('users:user-verify-wallet', kwargs={'pk': pk})
        self.user_stats_url = reverse('users:user-stats')
        self.user_search_url = reverse('users:user-search')
        self.user_notifications_url = lambda pk: reverse('users:user-notifications', kwargs={'pk': pk})
        self.user_roles_url = lambda pk: reverse('users:user-roles', kwargs={'pk': pk})
        self.user_reputation_url = lambda pk: reverse('users:user-reputation', kwargs={'pk': pk})
    
    def test_user_me_endpoint(self):
        """Test para el endpoint /me"""
        response = self.normal_client.get(self.user_me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'normaluser')
        self.assertEqual(response.data['email'], 'normal@example.com')
    
    def test_update_profile(self):
        """Test para actualizar perfil"""
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '+1234567890',
            'company': 'Test Company',
            'location': 'Test Location',
            'bio': 'This is a test bio'
        }
        
        response = self.normal_client.put(self.user_update_profile_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar actualización
        self.normal_user.refresh_from_db()
        self.assertEqual(self.normal_user.first_name, 'Updated')
        self.assertEqual(self.normal_user.phone_number, '+1234567890')
        self.assertEqual(self.normal_user.company, 'Test Company')
    
    def test_change_password_success(self):
        """Test para cambio de contraseña exitoso"""
        data = {
            'old_password': 'testpass123',
            'new_password': 'NewComplexPass123!',
            'new_password2': 'NewComplexPass123!'
        }
        
        response = self.normal_client.post(self.user_change_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que la contraseña cambió
        self.normal_user.refresh_from_db()
        self.assertTrue(self.normal_user.check_password('NewComplexPass123!'))
        
        # Verificar que se creó registro de actividad
        activity_log = UserActivityLog.objects.filter(
            user=self.normal_user,
            action='PASSWORD_CHANGE'
        ).first()
        self.assertIsNotNone(activity_log)
    
    def test_change_password_wrong_old_password(self):
        """Test para cambio de contraseña con contraseña antigua incorrecta"""
        data = {
            'old_password': 'wrongpassword',
            'new_password': 'NewComplexPass123!',
            'new_password2': 'NewComplexPass123!'
        }
        
        response = self.normal_client.post(self.user_change_password_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('old_password', response.data)
    
    def test_connect_wallet_success(self):
        """Test para conectar wallet exitosamente"""
        data = {
            'wallet_address': '0x1234567890abcdef1234567890abcdef12345678',
            'signature': '0x' + 'a' * 130,
            'message': 'Test message for signing'
        }
        
        response = self.normal_client.post(
            self.user_connect_wallet_url(self.normal_user.id),
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que la wallet se actualizó
        self.normal_user.refresh_from_db()
        self.assertEqual(self.normal_user.wallet_address, '0x1234567890abcdef1234567890abcdef12345678')
        
        # Verificar registro de actividad
        activity_log = UserActivityLog.objects.filter(
            user=self.normal_user,
            action='BLOCKCHAIN_INTERACTION'
        ).first()
        self.assertIsNotNone(activity_log)
        self.assertEqual(activity_log.metadata['action'], 'wallet_connect')
    
    def test_connect_wallet_duplicate_address(self):
        """Test para conectar wallet con dirección ya en uso"""
        # Primero conectar wallet a otro usuario
        self.other_user.wallet_address = '0x1234567890abcdef1234567890abcdef12345678'
        self.other_user.save()
        
        data = {
            'wallet_address': '0x1234567890abcdef1234567890abcdef12345678',
            'signature': '0x' + 'a' * 130,
            'message': 'Test message for signing'
        }
        
        response = self.normal_client.post(
            self.user_connect_wallet_url(self.normal_user.id),
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('wallet_address', response.data)
    
    def test_connect_wallet_permission_denied(self):
        """Test para conectar wallet a otro usuario sin permisos"""
        data = {
            'wallet_address': '0x1234567890abcdef1234567890abcdef12345678',
            'signature': '0x' + 'a' * 130,
            'message': 'Test message for signing'
        }
        
        # Usuario normal intentando modificar wallet de otro usuario
        response = self.normal_client.post(
            self.user_connect_wallet_url(self.other_user.id),
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_verify_wallet_success(self):
        """Test para verificar wallet exitosamente"""
        # Primero conectar una wallet
        self.normal_user.wallet_address = '0x1234567890abcdef1234567890abcdef12345678'
        self.normal_user.save()
        
        data = {
            'wallet_address': '0x1234567890abcdef1234567890abcdef12345678',
            'signed_message': '0x' + 'b' * 130,
            'original_message': 'Verification message'
        }
        
        response = self.normal_client.post(
            self.user_verify_wallet_url(self.normal_user.id),
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que el usuario está verificado
        self.normal_user.refresh_from_db()
        self.assertTrue(self.normal_user.is_verified)
        self.assertIsNotNone(self.normal_user.verification_date)
        
        # Verificar registro de actividad
        activity_log = UserActivityLog.objects.filter(
            user=self.normal_user,
            action='BLOCKCHAIN_INTERACTION'
        ).last()
        self.assertIsNotNone(activity_log)
        self.assertEqual(activity_log.metadata['action'], 'wallet_verification')
    
    def test_verify_wallet_address_mismatch(self):
        """Test para verificar wallet con dirección que no coincide"""
        self.normal_user.wallet_address = '0x1111111111111111111111111111111111111111'
        self.normal_user.save()
        
        data = {
            'wallet_address': '0x1234567890abcdef1234567890abcdef12345678',  # Diferente
            'signed_message': '0x' + 'b' * 130,
            'original_message': 'Verification message'
        }
        
        response = self.normal_client.post(
            self.user_verify_wallet_url(self.normal_user.id),
            data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_user_stats_admin_only(self):
        """Test que solo admin puede ver estadísticas"""
        # Usuario normal no puede acceder
        response = self.normal_client.get(self.user_stats_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Admin puede acceder
        response = self.admin_client.get(self.user_stats_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar estructura de datos
        self.assertIn('total_users', response.data)
        self.assertIn('active_users', response.data)
        self.assertIn('verified_users', response.data)
        self.assertIn('users_by_role', response.data)
    
    def test_user_search_admin_only(self):
        """Test que solo admin puede buscar usuarios"""
        data = {
            'query': 'test',
            'search_in': ['username', 'email']
        }
        
        # Usuario normal no puede buscar
        response = self.normal_client.get(self.user_search_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Admin puede buscar
        response = self.admin_client.get(self.user_search_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_user_notifications_access(self):
        """Test para acceder a notificaciones de usuario"""
        # Crear algunas notificaciones
        Notification.objects.create(
            user=self.normal_user,
            notification_type='HEALTH_ALERT',
            title='Test Notification',
            message='This is a test'
        )
        
        # Usuario puede ver sus propias notificaciones
        response = self.normal_client.get(self.user_notifications_url(self.normal_user.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Admin puede ver notificaciones de otros usuarios
        response = self.admin_client.get(self.user_notifications_url(self.normal_user.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Usuario normal no puede ver notificaciones de otros
        response = self.normal_client.get(self.user_notifications_url(self.other_user.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_user_roles_access(self):
        """Test para acceder a roles de usuario"""
        # Crear algunos roles
        UserRole.objects.create(
            user=self.normal_user,
            role_type='PRODUCER_ROLE',
            scope_type='GLOBAL'
        )
        
        # Usuario puede ver sus propios roles
        response = self.normal_client.get(self.user_roles_url(self.normal_user.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Admin puede ver roles de otros usuarios
        response = self.admin_client.get(self.user_roles_url(self.normal_user.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Usuario normal no puede ver roles de otros
        response = self.normal_client.get(self.user_roles_url(self.other_user.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_user_reputation_access(self):
        """Test para acceder a reputación de usuario"""
        # Crear puntuación de reputación
        ReputationScore.objects.create(
            user=self.normal_user,
            reputation_type='PRODUCER',
            score=4.5,
            total_actions=10,
            positive_actions=9
        )
        
        # Usuario puede ver su propia reputación
        response = self.normal_client.get(self.user_reputation_url(self.normal_user.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Admin puede ver reputación de otros usuarios
        response = self.admin_client.get(self.user_reputation_url(self.normal_user.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Usuario normal no puede ver reputación de otros
        response = self.normal_client.get(self.user_reputation_url(self.other_user.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PasswordResetTests(APITestCase):
    """Tests para reset de contraseña"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            wallet_address='0x1111111111111111111111111111111111111111'
        )
        
        self.password_reset_url = reverse('users:password-reset')
        self.password_reset_confirm_url = reverse('users:password-reset-confirm')
    
    def test_password_reset_request(self):
        """Test para solicitar reset de contraseña"""
        data = {'email': 'test@example.com'}
        response = self.client.post(self.password_reset_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
    
    def test_password_reset_request_nonexistent_email(self):
        """Test para solicitar reset con email inexistente"""
        data = {'email': 'nonexistent@example.com'}
        response = self.client.post(self.password_reset_url, data, format='json')
        
        # Debería devolver éxito por seguridad (no revelar si el email existe)
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
        self.assertIn('message', response.data)
    
    def test_password_reset_confirm_password_mismatch(self):
        """Test para confirmar reset con contraseñas que no coinciden"""
        data = {
            'token': 'test-token-123',
            'new_password': 'NewPass123!',
            'new_password2': 'DifferentPass123!'
        }
        
        response = self.client.post(self.password_reset_confirm_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('new_password', response.data)


class UserProfileViewTests(APITestCase):
    """Tests para la vista legacy de perfil de usuario"""
    
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
        
        self.profile_url = reverse('users:user-profile')
    
    def test_get_user_profile_legacy(self):
        """Test para obtener perfil (vista legacy)"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_update_user_profile_legacy(self):
        """Test para actualizar perfil (vista legacy)"""
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '+1234567890'
        }
        
        response = self.client.put(self.profile_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar actualización
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.phone_number, '+1234567890')


class WalletConnectViewTests(APITestCase):
    """Tests para la vista de conexión de wallet"""
    
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
        
        self.wallet_connect_url = reverse('users:wallet-connect')
    
    def test_wallet_connect_success(self):
        """Test para conectar wallet exitosamente"""
        data = {
            'wallet_address': '0x1234567890abcdef1234567890abcdef12345678'
        }
        
        response = self.client.post(self.wallet_connect_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertTrue(response.data['success'])
        
        # Verificar que la wallet se actualizó
        self.user.refresh_from_db()
        self.assertEqual(self.user.wallet_address, '0x1234567890abcdef1234567890abcdef12345678')
    
    def test_wallet_connect_invalid_address(self):
        """Test para conectar wallet con dirección inválida"""
        data = {
            'wallet_address': 'invalid-address'
        }
        
        response = self.client.post(self.wallet_connect_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_wallet_connect_missing_address(self):
        """Test para conectar wallet sin dirección"""
        data = {}
        
        response = self.client.post(self.wallet_connect_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class UserPermissionEdgeCasesTests(APITestCase):
    """Tests para casos edge de permisos de usuario"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Crear usuario normal
        self.normal_user = User.objects.create_user(
            username='normaluser',
            email='normal@example.com',
            password='testpass123',
            wallet_address='0x2222222222222222222222222222222222222222'
        )
        
        # Crear otro usuario
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123',
            wallet_address='0x3333333333333333333333333333333333333333'
        )
        
        refresh_normal = RefreshToken.for_user(self.normal_user)
        self.normal_client = APIClient()
        self.normal_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh_normal.access_token}')
    
    def test_user_cannot_access_other_user_detail(self):
        """Test que usuario no puede acceder a detalles de otro usuario"""
        url = reverse('users:user-detail', kwargs={'pk': self.other_user.id})
        response = self.normal_client.get(url)
        
        # Debería devolver 404 por seguridad (no revelar existencia)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_user_cannot_update_other_user(self):
        """Test que usuario no puede actualizar otro usuario"""
        url = reverse('users:user-detail', kwargs={'pk': self.other_user.id})
        update_data = {'first_name': 'Hacked'}
        
        response = self.normal_client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_user_cannot_delete_other_user(self):
        """Test que usuario no puede eliminar otro usuario"""
        url = reverse('users:user-detail', kwargs={'pk': self.other_user.id})
        
        response = self.normal_client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UserViewSetPaginationTests(APITestCase):
    """Tests para paginación y filtros de UserViewSet"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Crear admin user
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpass123',
            wallet_address='0x1111111111111111111111111111111111111111',
            is_staff=True
        )
        
        refresh_admin = RefreshToken.for_user(self.admin_user)
        self.admin_client = APIClient()
        self.admin_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh_admin.access_token}')
        
        # Crear múltiples usuarios para testing
        for i in range(15):
            User.objects.create_user(
                username=f'testuser{i}',
                email=f'test{i}@example.com',
                password=f'testpass{i}',
                wallet_address=f'0x{str(i).zfill(40)}',
                role='PRODUCER' if i % 2 == 0 else 'VET'
            )
        
        self.user_list_url = reverse('users:user-list')
    
    def test_user_list_pagination(self):
        """Test que la lista de usuarios está paginada"""
        response = self.admin_client.get(self.user_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)
        
        # Verificar que hay múltiples páginas
        self.assertGreater(response.data['count'], 10)
        self.assertIsNotNone(response.data['next'])
    
    def test_user_filter_by_role(self):
        """Test para filtrar usuarios por rol"""
        response = self.admin_client.get(self.user_list_url, {'role': 'PRODUCER'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Todos los usuarios en los resultados deberían ser productores
        for user in response.data['results']:
            self.assertEqual(user['role'], 'PRODUCER')
    
    def test_user_filter_by_verification_status(self):
        """Test para filtrar usuarios por estado de verificación"""
        # Marcar algunos usuarios como verificados
        users_to_verify = User.objects.filter(role='PRODUCER')[:3]
        for user in users_to_verify:
            user.is_verified = True
            user.save()
        
        response = self.admin_client.get(self.user_list_url, {'is_verified': 'true'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Todos los usuarios en los resultados deberían estar verificados
        for user in response.data['results']:
            self.assertTrue(user['is_verified'])
    
    def test_user_search_functionality(self):
        """Test para funcionalidad de búsqueda"""
        # Crear usuario con nombre específico
        User.objects.create_user(
            username='johndoe',
            email='john@example.com',
            password='testpass123',
            wallet_address='0x9999999999999999999999999999999999999999',
            first_name='John',
            last_name='Doe',
            company='Doe Enterprises'
        )
        
        # Buscar por username
        response = self.admin_client.get(self.user_list_url, {'search': 'johndoe'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['username'], 'johndoe')
        
        # Buscar por email
        response = self.admin_client.get(self.user_list_url, {'search': 'john@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Buscar por nombre
        response = self.admin_client.get(self.user_list_url, {'search': 'John'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
        
        # Buscar por empresa
        response = self.admin_client.get(self.user_list_url, {'search': 'Doe Enterprises'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)