"""
Tests extendidos para blockchain/views.py - Para mejorar cobertura
"""
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch, MagicMock
from cattle.models import Animal

User = get_user_model()

class BlockchainViewsExtendedTests(APITestCase):
    """Tests extendidos para blockchain views - Mejorar cobertura"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = APIClient()
        
        # Crear usuario con diferentes roles
        self.admin_user = User.objects.create_user(
            username='blockchainadmin',
            email='admin@example.com',
            password='adminpass',
            wallet_address='0xAdminAddress12345678901234567890123456789012',
            role='ADMIN'
        )
        
        self.farmer_user = User.objects.create_user(
            username='blockchainfarmer',
            email='farmer@example.com',
            password='farmerpass',
            wallet_address='0xFarmerAddress123456789012345678901234567890',
            role='FARMER'
        )
        
        # Crear animal con IPFS hash para tests de NFT
        self.animal = Animal.objects.create(
            ear_tag='NFTTEST001',
            breed='Angus',
            birth_date='2023-01-01',
            owner=self.farmer_user,
            ipfs_hash='QmTestNFTHash123456789',
            weight=500.0,
            health_status='HEALTHY'
        )
    
    @patch('blockchain.views.BlockchainService')
    def test_mint_nft_success(self, mock_service):
        """Test para mint NFT exitoso"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Configurar mock
        mock_instance = MagicMock()
        mock_instance.mint_and_associate_animal.return_value = {
            'success': True,
            'tx_hash': '0xNftTxHash123',
            'animal_id': self.animal.id
        }
        mock_service.return_value = mock_instance
        
        url = reverse('blockchain:mint-nft')
        data = {
            'animal_id': self.animal.id,
            'owner_wallet': self.farmer_user.wallet_address
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['tx_hash'], '0xNftTxHash123')
        mock_instance.mint_and_associate_animal.assert_called_once()
    
    @patch('blockchain.views.BlockchainService')
    def test_mint_nft_animal_not_found(self, mock_service):
        """Test para mint NFT con animal no existente"""
        self.client.force_authenticate(user=self.admin_user)
        
        mock_instance = MagicMock()
        mock_service.return_value = mock_instance
        
        url = reverse('blockchain:mint-nft')
        data = {
            'animal_id': 9999,  # ID que no existe
            'owner_wallet': self.farmer_user.wallet_address
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('animal_id', response.data)
    
    @patch('blockchain.views.BlockchainService')
    def test_assign_role_success(self, mock_service):
        """Test para asignación de rol exitosa"""
        self.client.force_authenticate(user=self.admin_user)
        
        mock_instance = MagicMock()
        mock_instance.assign_role.return_value = '0xRoleTxHash123'
        mock_service.return_value = mock_instance
        
        url = reverse('blockchain:assign-role')
        data = {
            'target_wallet': '0xNewUser1234567890123456789012345678901234',
            'role_name': 'PRODUCER'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['tx_hash'], '0xRoleTxHash123')
        mock_instance.assign_role.assert_called_once()
    
    @patch('blockchain.views.BlockchainService')
    def test_assign_role_invalid_wallet(self, mock_service):
        """Test para asignación de rol con wallet inválida"""
        self.client.force_authenticate(user=self.admin_user)
        
        mock_instance = MagicMock()
        mock_instance.assign_role.side_effect = Exception('Invalid wallet')
        mock_service.return_value = mock_instance
        
        url = reverse('blockchain:assign-role')
        data = {
            'target_wallet': 'invalid-wallet-address',
            'role_name': 'PRODUCER'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('target_wallet', response.data)
    
    @patch('blockchain.views.BlockchainService')
    def test_has_role_check(self, mock_service):
        """Test para verificación de rol"""
        self.client.force_authenticate(user=self.admin_user)
        
        mock_instance = MagicMock()
        mock_instance.has_role.return_value = True
        mock_service.return_value = mock_instance
        
        url = reverse('blockchain:has-role')
        params = {
            'wallet': self.farmer_user.wallet_address,
            'role': 'FARMER'
        }
        
        response = self.client.get(url, params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['has_role'])
        mock_instance.has_role.assert_called_once()
    
    @patch('blockchain.views.BlockchainService')
    def test_get_balance(self, mock_service):
        """Test para obtener balance de wallet"""
        self.client.force_authenticate(user=self.admin_user)
        
        mock_instance = MagicMock()
        mock_instance.get_balance.return_value = 1000000000000000000  # 1 ETH
        mock_service.return_value = mock_instance
        
        url = reverse('blockchain:get-balance')
        params = {'wallet': self.farmer_user.wallet_address}
        
        response = self.client.get(url, params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['balance'], 1000000000000000000)
        mock_instance.get_balance.assert_called_once()
    
    @patch('blockchain.views.BlockchainService')
    def test_mint_tokens(self, mock_service):
        """Test para mint de tokens ERC20"""
        self.client.force_authenticate(user=self.admin_user)
        
        mock_instance = MagicMock()
        mock_instance.mint_tokens.return_value = '0xTokenTxHash123'
        mock_service.return_value = mock_instance
        
        url = reverse('blockchain:mint-tokens')
        data = {
            'to_address': self.farmer_user.wallet_address,
            'amount': '1000'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['tx_hash'], '0xTokenTxHash123')
        mock_instance.mint_tokens.assert_called_once()
    
    @patch('blockchain.views.BlockchainService')
    def test_get_token_balance(self, mock_service):
        """Test para obtener balance de tokens"""
        self.client.force_authenticate(user=self.admin_user)
        
        mock_instance = MagicMock()
        mock_instance.get_token_balance.return_value = 500
        mock_service.return_value = mock_instance
        
        url = reverse('blockchain:token-balance')
        params = {'wallet': self.farmer_user.wallet_address}
        
        response = self.client.get(url, params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['balance'], 500)
        mock_instance.get_token_balance.assert_called_once()
    
    @patch('blockchain.views.BlockchainService')
    def test_get_animal_nft_info(self, mock_service):
        """Test para obtener información de NFT de animal"""
        self.client.force_authenticate(user=self.admin_user)
        
        mock_instance = MagicMock()
        mock_instance.get_animal_nft_info.return_value = {
            'token_id': 123,
            'owner': self.farmer_user.wallet_address,
            'token_uri': 'ipfs://QmTestHash'
        }
        mock_service.return_value = mock_instance
        
        # Asignar token_id al animal
        self.animal.token_id = 123
        self.animal.save()
        
        url = reverse('blockchain:animal-nft-info', kwargs={'animal_id': self.animal.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['token_id'], 123)
        mock_instance.get_animal_nft_info.assert_called_once()
    
    @patch('blockchain.views.BlockchainService')
    def test_verify_animal_nft(self, mock_service):
        """Test para verificación de NFT de animal"""
        self.client.force_authenticate(user=self.admin_user)
        
        mock_instance = MagicMock()
        mock_instance.verify_animal_nft.return_value = {
            'verified': True,
            'owner_matches': True,
            'ipfs_in_uri': True
        }
        mock_service.return_value = mock_instance
        
        url = reverse('blockchain:verify-animal-nft', kwargs={'animal_id': self.animal.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['verified'])
        mock_instance.verify_animal_nft.assert_called_once()

class BlockchainViewsPermissionTests(APITestCase):
    """Tests de permisos para blockchain views"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Crear usuarios con diferentes roles
        self.admin = User.objects.create_user(
            username='admin', password='pass', role='ADMIN',
            wallet_address='0xAdmin1234567890123456789012345678901234'
        )
        
        self.farmer = User.objects.create_user(
            username='farmer', password='pass', role='FARMER',
            wallet_address='0xFarmer1234567890123456789012345678901234'
        )
        
        self.producer = User.objects.create_user(
            username='producer', password='pass', role='PRODUCER', 
            wallet_address='0xProducer12345678901234567890123456789012'
        )
    
    def test_mint_nft_permission_admin(self):
        """Test que admin puede mint NFT"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('blockchain:mint-nft')
        
        response = self.client.get(url)  # GET para probar acceso
        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_mint_nft_permission_farmer_denied(self):
        """Test que farmer NO puede mint NFT"""
        self.client.force_authenticate(user=self.farmer)
        url = reverse('blockchain:mint-nft')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_assign_role_permission_admin(self):
        """Test que admin puede asignar roles"""
        self.client.force_authenticate(user=self.admin)
        url = reverse('blockchain:assign-role')
        
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_assign_role_permission_producer_denied(self):
        """Test que producer NO puede asignar roles"""
        self.client.force_authenticate(user=self.producer)
        url = reverse('blockchain:assign-role')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_has_role_access_public(self):
        """Test que verificación de roles es pública"""
        url = reverse('blockchain:has-role')
        params = {'wallet': self.farmer.wallet_address, 'role': 'FARMER'}
        
        response = self.client.get(url, params)
        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)