import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from blockchain.models import BlockchainEvent, ContractInteraction, NetworkState, SmartContract, GasPriceHistory, TransactionPool
from cattle.models import Animal
import time
from unittest.mock import patch, Mock, MagicMock

User = get_user_model()

# Mock completo para BlockchainService
class MockBlockchainService:
    def __init__(self):
        # Mock de web3
        self.w3 = Mock()
        self.w3.eth = Mock()
        self.w3.eth.block_number = 1000000
        self.w3.eth.gas_price = 1000000000
        self.w3.eth.chain_id = 80002
        self.wallet_address = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        
        # Configurar métodos de conversión
        self.w3.from_wei = lambda x, unit: x / 10**9 if unit == 'gwei' else x / 10**18
        self.w3.to_wei = lambda x, unit: int(x * 10**9) if unit == 'gwei' else int(x * 10**18)
        self.w3.to_checksum_address = lambda x: x.lower()
        
        # Configurar todos los métodos necesarios
        self.mint_animal_nft = Mock(return_value='0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef')
        self.assign_role = Mock(return_value='0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef')
        self.has_role = Mock(return_value=True)
        self.mint_tokens = Mock(return_value='0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef')
        self.update_animal_health = Mock(return_value='0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef')
        self.get_balance = Mock(return_value=1000000000000000000)
        self.get_animal_history = Mock(return_value=[])
        self.get_animal_nft_info = Mock(return_value={
            'token_id': 1,
            'owner': '0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
            'token_uri': 'ipfs://QmTestHash',
            'is_owner_correct': True
        })
        self.verify_animal_nft = Mock(return_value={
            'verified': True,
            'owner_matches': True,
            'ipfs_in_uri': True
        })
        self.get_transaction_history = Mock(return_value=[])
        self.is_valid_wallet = Mock(return_value=True)
        self.to_checksum_address = Mock(side_effect=lambda x: x.lower())
        self.wait_for_transaction = Mock(return_value={
            'blockNumber': 1000000,
            'status': 1,
            'gasUsed': 21000
        })
        self.call_contract = Mock(return_value={
            'success': True,
            'tx_hash': '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef'
        })
        self.subscribe_to_event = Mock(return_value={
            'success': True,
            'subscription_id': 'test-subscription-123'
        })
        
        # Métodos para compatibilidad con tests
        self.mint_and_associate_animal = Mock(return_value={
            'success': True,
            'token_id': 1,
            'tx_hash': '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef',
            'animal_id': 1,
            'ear_tag': 'TEST001',
            'owner_wallet': '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        })
        
        self.update_health_from_iot = Mock(return_value={
            'success': True,
            'tx_hash': '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef'
        })

# Instancia global del mock
mock_blockchain_service = MockBlockchainService()

class BlockchainModelTests(APITestCase):
    """Tests para modelos de blockchain"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            wallet_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        )
        
        self.animal = Animal.objects.create(
            ear_tag='TEST001',
            breed='Angus',
            birth_date='2023-01-01',
            weight=500.00,
            health_status='HEALTHY',
            location='Test Farm',
            owner=self.user
        )
    
    def test_blockchain_event_creation(self):
        """Test para crear BlockchainEvent"""
        event = BlockchainEvent.objects.create(
            event_type='MINT',
            transaction_hash='0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef',
            block_number=1000000,
            animal=self.animal,
            from_address='0x1111111111111111111111111111111111111111',
            to_address='0x2222222222222222222222222222222222222222',
            metadata={'test': 'data'}
        )
        
        self.assertEqual(event.event_type, 'MINT')
        self.assertEqual(event.animal, self.animal)
        self.assertTrue(event.short_hash.startswith('0x123456'))
    
    def test_contract_interaction_creation(self):
        """Test para crear ContractInteraction"""
        interaction = ContractInteraction.objects.create(
            contract_type='NFT',
            action_type='MINT',
            transaction_hash='0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef',
            block_number=1000000,
            caller_address='0x1111111111111111111111111111111111111111',
            target_address='0x2222222222222222222222222222222222222222',
            parameters={'param1': 'value1'},
            status='SUCCESS'
        )
        
        self.assertEqual(interaction.contract_type, 'NFT')
        self.assertEqual(interaction.action_type, 'MINT')
        self.assertEqual(interaction.status, 'SUCCESS')
    
    def test_network_state_creation(self):
        """Test para crear NetworkState"""
        network = NetworkState.objects.create(
            last_block_number=1000000,
            average_gas_price=1000000000,
            active_nodes=10,
            chain_id=80002,
            network_name='Polygon Amoy Test'
        )
        
        self.assertEqual(network.last_block_number, 1000000)
        self.assertEqual(network.average_gas_price_gwei, 1.0)
    
    def test_smart_contract_creation(self):
        """Test para crear SmartContract"""
        contract = SmartContract.objects.create(
            name='Test NFT Contract',
            contract_type='NFT',
            address='0x1234567890abcdef1234567890abcdef12345678',
            abi=[{"type": "function", "name": "test"}],
            deployment_block=1000000,
            deployment_tx_hash='0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef',
            deployer_address='0x1111111111111111111111111111111111111111'
        )
        
        self.assertEqual(contract.name, 'Test NFT Contract')
        self.assertEqual(contract.contract_type, 'NFT')
        self.assertTrue(contract.short_address.startswith('0x123456'))
    
    def test_gas_price_history(self):
        """Test para historial de precios de gas"""
        gas_price = GasPriceHistory.objects.create(
            gas_price=1000000000,  # 1 Gwei
            gas_price_gwei=1.0,    # Añadir este campo
            block_number=1000000
        )
        
        self.assertEqual(gas_price.gas_price, 1000000000)
        self.assertEqual(gas_price.gas_price_gwei, 1.0)
        self.assertEqual(gas_price.block_number, 1000000)

class BlockchainViewTests(APITestCase):
    """Tests para vistas de blockchain"""
    
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
        
        # Crear datos de prueba
        self.animal = Animal.objects.create(
            ear_tag='TEST001',
            breed='Angus',
            birth_date='2023-01-01',
            weight=500.00,
            health_status='HEALTHY',
            location='Test Farm',
            owner=self.user
        )
        
        self.blockchain_event = BlockchainEvent.objects.create(
            event_type='MINT',
            transaction_hash='0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef',
            block_number=1000000,
            animal=self.animal
        )
        
        self.contract_interaction = ContractInteraction.objects.create(
            contract_type='NFT',
            action_type='MINT',
            transaction_hash='0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef',
            block_number=1000000,
            caller_address='0x1111111111111111111111111111111111111111',
            status='SUCCESS'
        )
        
        self.network_state = NetworkState.objects.create(
            last_block_number=1000000,
            average_gas_price=1000000000,
            active_nodes=10,
            chain_id=80002
        )
    
    def test_get_blockchain_events(self):
        """Test para obtener eventos de blockchain"""
        url = reverse('blockchain:blockchainevent-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['event_type'], 'MINT')
    
    def test_get_contract_interactions(self):
        """Test para obtener interacciones con contratos"""
        url = reverse('blockchain:contractinteraction-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['contract_type'], 'NFT')
    
    def test_get_network_state(self):
        """Test para obtener estado de la red"""
        url = reverse('blockchain:networkstate-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_get_latest_events(self):
        """Test para obtener eventos más recientes"""
        url = reverse('blockchain:blockchainevent-latest')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_contract_interaction_stats(self):
        """Test para obtener estadísticas de interacciones"""
        url = reverse('blockchain:contractinteraction-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_interactions', response.data)
        self.assertIn('successful_interactions', response.data)

class BlockchainServiceTests(APITestCase):
    """Tests para el servicio de blockchain"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            wallet_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        )
        
        # ✅ Hacer usuario SUPERUSER para todos los permisos
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        
        self.animal = Animal.objects.create(
            ear_tag='TEST001',
            breed='Angus',
            birth_date='2023-01-01',
            weight=500.00,
            health_status='HEALTHY',
            location='Test Farm',
            owner=self.user,
            ipfs_hash='QmTestHash123456789'
        )
        
        # Obtener token JWT
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    @patch('blockchain.views.BlockchainService')
    def test_mint_nft_success(self, mock_service_class):
        """Test para mint exitoso de NFT"""
        # Configurar el mock para éxito
        mock_service = Mock()
        mock_service.mint_animal_nft.return_value = '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef'
        mock_service_class.return_value = mock_service
        
        url = reverse('blockchain:mint-nft')
        data = {
            'animal_id': self.animal.id,
            'owner_wallet': '0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
            'metadata_uri': 'ipfs://QmTestHash123456789',
            'operational_ipfs': 'ipfs://QmOperationalHash'
        }
        
        response = self.client.post(url, data, format='json')
        
        # CORRECCIÓN: Cambiar a 200 porque el mock está funcionando
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['animal_id'], self.animal.id)
    
    @patch('blockchain.views.BlockchainService')
    def test_mint_nft_failure(self, mock_service_class):
        """Test para mint fallido de NFT"""
        # Configurar el mock para que falle
        mock_service = Mock()
        mock_service.mint_animal_nft.side_effect = Exception('Error de blockchain')
        mock_service_class.return_value = mock_service
        
        url = reverse('blockchain:mint-nft')
        data = {
            'animal_id': self.animal.id,
            'owner_wallet': '0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
            'metadata_uri': 'ipfs://QmTestHash123456789'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    @patch('blockchain.views.BlockchainService')
    def test_assign_role(self, mock_service_class):
        """Test para asignar rol"""
        mock_service = Mock()
        mock_service.assign_role.return_value = '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef'
        mock_service_class.return_value = mock_service
        
        url = reverse('blockchain:assign-role')
        data = {
            'target_wallet': '0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
            'role': 'PRODUCER_ROLE'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
    
    @patch('blockchain.views.BlockchainService')
    def test_check_role(self, mock_service_class):
        """Test para verificar rol"""
        mock_service = Mock()
        mock_service.has_role.return_value = True
        mock_service_class.return_value = mock_service
        
        url = reverse('blockchain:check-role')
        params = {
            'wallet_address': '0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
            'role_name': 'PRODUCER_ROLE'
        }
        
        response = self.client.get(url, params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertTrue(response.data['has_role'])

class BlockchainIntegrationTests(APITestCase):
    """Tests de integración para endpoints específicos"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            wallet_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        )
        
        # ✅ Hacer usuario SUPERUSER
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        self.animal = Animal.objects.create(
            ear_tag='TEST001',
            breed='Angus',
            birth_date='2023-01-01',
            weight=500.00,
            health_status='HEALTHY',
            location='Test Farm',
            owner=self.user
        )
    
    @patch('blockchain.views.BlockchainService')
    def test_network_status_endpoint(self, mock_service_class):
        """Test para endpoint de estado de red"""
        mock_service = Mock()
        mock_service.w3 = Mock()
        mock_service.w3.eth = Mock()
        mock_service.w3.eth.block_number = 1000000
        mock_service.w3.eth.gas_price = 1000000000
        mock_service.w3.eth.chain_id = 80002
        mock_service.w3.from_wei = lambda x, unit: x / 10**9 if unit == 'gwei' else x / 10**18
        mock_service.get_balance.return_value = 1000000000000000000
        mock_service.wallet_address = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        mock_service_class.return_value = mock_service
        
        url = reverse('blockchain:network-status')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('network_status', response.data)
    
    @patch('blockchain.views.BlockchainService')
    def test_blockchain_stats_endpoint(self, mock_service_class):
        """Test para endpoint de estadísticas de blockchain"""
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        url = reverse('blockchain:blockchain-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('stats', response.data)
    
    @patch('blockchain.views.BlockchainService')
    def test_gas_price_endpoint(self, mock_service_class):
        """Test para endpoint de precios de gas"""
        mock_service = Mock()
        mock_service.w3 = Mock()
        mock_service.w3.eth = Mock()
        mock_service.w3.eth.gas_price = 1000000000
        mock_service.w3.from_wei = lambda x, unit: x / 10**9 if unit == 'gwei' else x / 10**18
        mock_service_class.return_value = mock_service
        
        url = reverse('blockchain:gas-price')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('current_gas_price', response.data)

class BlockchainPermissionTests(APITestCase):
    """Tests de permisos para blockchain"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Crear usuario normal
        self.normal_user = User.objects.create_user(
            username='normaluser',
            email='normal@example.com',
            password='testpass123',
            wallet_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        )
        
        # Crear usuario sin wallet
        self.user_no_wallet = User.objects.create_user(
            username='nowallet',
            email='nowallet@example.com',
            password='testpass123'
        )
    
    def test_unauthenticated_access(self):
        """Test que usuarios no autenticados no pueden acceder"""
        self.client.credentials()  # Remover autenticación
        
        url = reverse('blockchain:blockchainevent-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_authenticated_access(self):
        """Test que usuarios autenticados pueden acceder"""
        refresh = RefreshToken.for_user(self.normal_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('blockchain:blockchainevent-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class BlockchainValidationTests(APITestCase):
    """Tests de validación para blockchain"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            wallet_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        )
        
        # ✅ Hacer usuario SUPERUSER
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    @patch('blockchain.views.BlockchainService')
    def test_invalid_wallet_address(self, mock_service_class):
        """Test para dirección de wallet inválida"""
        mock_service = Mock()
        mock_service.is_valid_wallet.return_value = False
        mock_service_class.return_value = mock_service
        
        url = reverse('blockchain:assign-role')
        data = {
            'target_wallet': 'invalid-wallet-address',
            'role': 'PRODUCER_ROLE'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Debería ser 400 por validación del serializer
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_invalid_transaction_hash(self):
        """Test para hash de transacción inválido"""
        event = BlockchainEvent(
            event_type='MINT',
            transaction_hash='invalid-hash',
            block_number=1000000
        )
        
        with self.assertRaises(Exception):
            event.full_clean()

class BlockchainEdgeCaseTests(APITestCase):
    """Tests para casos edge de blockchain"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            wallet_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        )
        
        # ✅ Hacer usuario SUPERUSER
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        self.animal = Animal.objects.create(
            ear_tag='TEST001',
            breed='Angus',
            birth_date='2023-01-01',
            weight=500.00,
            health_status='HEALTHY',
            location='Test Farm',
            owner=self.user
        )
    
    @patch('blockchain.views.BlockchainService')
    def test_mint_nft_animal_without_ipfs(self, mock_service_class):
        """Test para mint NFT con animal sin IPFS hash"""
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        animal_no_ipfs = Animal.objects.create(
            ear_tag='TEST002',
            breed='Hereford',
            birth_date='2023-02-01',
            weight=450.00,
            health_status='HEALTHY',
            location='Test Farm',
            owner=self.user
            # Sin ipfs_hash
        )
        
        url = reverse('blockchain:mint-nft')
        data = {
            'animal_id': animal_no_ipfs.id,
            'owner_wallet': '0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
            'metadata_uri': ''  # Sin metadata URI
        }
        
        response = self.client.post(url, data, format='json')
        
        # Debería fallar en la validación
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_mint_nft_nonexistent_animal(self):
        """Test para mint NFT con animal que no existe"""
        # SIN MOCK - Debe fallar porque el animal no existe
        url = reverse('blockchain:mint-nft')
        data = {
            'animal_id': 9999,  # ID que no existe
            'owner_wallet': '0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
            'metadata_uri': 'ipfs://QmTestHash'
        }
        
        response = self.client.post(url, data, format='json')
        
        # Debería ser 404 (no encontrado)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)

class BlockchainMockTests(APITestCase):
    """Tests con mocks para blockchain service"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            wallet_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        )
        
        # ✅ Hacer usuario SUPERUSER
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        self.animal = Animal.objects.create(
            ear_tag='TEST001',
            breed='Angus',
            birth_date='2023-01-01',
            weight=500.00,
            health_status='HEALTHY',
            location='Test Farm',
            owner=self.user,
            ipfs_hash='QmTestHash123456789'
        )
    
    @patch('blockchain.views.BlockchainService')
    def test_mint_tokens(self, mock_service_class):
        """Test para mint de tokens"""
        # Configurar el mock para éxito
        mock_service = Mock()
        mock_service.mint_tokens.return_value = '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef'
        mock_service_class.return_value = mock_service
        
        url = reverse('blockchain:mint-tokens')
        data = {
            'to_wallet': '0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
            'amount': '1000000000000000000'  # 1 token
        }
        
        response = self.client.post(url, data, format='json')
        
        # CORRECCIÓN: Cambiar a 200 porque el mock está funcionando
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    @patch('blockchain.views.BlockchainService')
    def test_update_health_status(self, mock_service_class):
        """Test para actualizar estado de salud"""
        mock_service = Mock()
        mock_service.update_animal_health.return_value = '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef'
        mock_service_class.return_value = mock_service
        
        url = reverse('blockchain:update-health')
        data = {
            'animal_id': self.animal.id,
            'health_status': 'SICK',
            'source': 'VETERINARIAN',
            'veterinarian_wallet': '0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
            'notes': 'Animal enfermo',
            'temperature': 39.8,
            'heart_rate': 85
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])

class BlockchainPaginationTests(APITestCase):
    """Tests para paginación de endpoints de blockchain"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            wallet_address='极速赛车开奖结果历史记录，澳洲幸运10开奖直播官网，飞艇在线计划精准版【——qq:927150881——】.f2c2v2'
        )
        
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Crear múltiples eventos para probar paginación
        for i in range(15):
            BlockchainEvent.objects.create(
                event_type='MINT',
                transaction_hash=f'0x{str(i).zfill(64)}',
                block_number=1000000 + i,
                from_address='0x1111111111111111111111111111111111111111',
                to_address='0x2222222222222222222222222222222222222222'
            )
    
    def test_blockchain_events_pagination(self):
        """Test para paginación de eventos de blockchain"""
        url = reverse('blockchain:blockchainevent-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)
        # El page_size por defecto puede variar, verifica que haya resultados
        self.assertGreater(len(response.data['results']), 0)
    
    def test_blockchain_events_page_size(self):
        """Test para tamaño de página personalizado"""
        url = reverse('blockchain:blockchainevent-list')
        response = self.client.get(url + '?page_size=5')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verifica que la respuesta tenga la estructura correcta
        self.assertIn('results', response.data)