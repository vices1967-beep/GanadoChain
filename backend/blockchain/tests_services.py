"""
Tests específicos para blockchain/services.py - VERSIÓN FINAL CORREGIDA
"""
from django.test import TestCase
from unittest.mock import patch, MagicMock
from django.conf import settings

# Importar el servicio
from blockchain.services import BlockchainService

# Mock provider válido
class MockProvider:
    def __init__(self):
        pass
    
    def is_connected(self):
        return True

class BlockchainServicesTests(TestCase):
    """Tests para BlockchainService - VERSIÓN FINAL CORREGIDA"""
    
    def setUp(self):
        """Configuración inicial"""
        # Guardar settings originales
        self.original_settings = {
            'BLOCKCHAIN_RPC_URL': getattr(settings, 'BLOCKCHAIN_RPC_URL', ''),
            'ADMIN_PRIVATE_KEY': getattr(settings, 'ADMIN_PRIVATE_KEY', ''),
            'GANADO_TOKEN_ADDRESS': getattr(settings, 'GANADO_TOKEN_ADDRESS', ''),
            'ANIMAL_NFT_ADDRESS': getattr(settings, 'ANIMAL_NFT_ADDRESS', ''),
            'REGISTRY_ADDRESS': getattr(settings, 'REGISTRY_ADDRESS', ''),
        }
        
        # Configurar settings de prueba
        settings.BLOCKCHAIN_RPC_URL = 'https://test.rpc.url'
        settings.ADMIN_PRIVATE_KEY = 'test-private-key-0000000000000000000000000000000000000000000000000000000000000000'
        settings.GANADO_TOKEN_ADDRESS = '0x' + '1' * 40
        settings.ANIMAL_NFT_ADDRESS = '0x' + '2' * 40  
        settings.REGISTRY_ADDRESS = '0x' + '3' * 40
    
    def tearDown(self):
        """Restaurar settings originales"""
        for key, value in self.original_settings.items():
            setattr(settings, key, value)
    
    @patch('blockchain.services.Web3')
    def test_service_initialization_success(self, mock_web3):
        """Test que el servicio se inicializa correctamente"""
        # Configurar mocks
        mock_w3_instance = MagicMock()
        mock_web3.return_value = mock_w3_instance
        
        # Mock para la cuenta
        mock_account = MagicMock()
        mock_account.address = '0xAdminAddress'
        mock_w3_instance.eth.account.from_key.return_value = mock_account
        
        # Mock para HTTPProvider
        mock_w3_instance.HTTPProvider.return_value = MockProvider()
        
        with patch('blockchain.services.BlockchainService.load_contracts'):
            service = BlockchainService()
            
            self.assertIsNotNone(service)
            self.assertEqual(service.wallet_address, '0xAdminAddress')
    
    def test_service_initialization_missing_private_key(self):
        """Test que falla cuando no hay ADMIN_PRIVATE_KEY"""
        original_key = getattr(settings, 'ADMIN_PRIVATE_KEY', '')
        settings.ADMIN_PRIVATE_KEY = ''
        
        with self.assertRaises(ValueError) as context:
            BlockchainService()
        
        self.assertIn('ADMIN_PRIVATE_KEY no está configurada', str(context.exception))
        
        # Restaurar
        settings.ADMIN_PRIVATE_KEY = original_key
    
    @patch('blockchain.services.Web3')
    def test_get_role_hash(self, mock_web3):
        """Test para get_role_hash - CORREGIDO"""
        # Configurar el mock para que devuelva bytes reales
        hash_esperado = b'\x9f\x12\xa1\x9a\x1b\xcd\xef\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        
        # Usar mock_web3 en lugar de self.mock_web3
        mock_web3.keccak.return_value = hash_esperado
        
        # Crear instancia del servicio (necesitas inicializar el servicio)
        mock_w3_instance = MagicMock()
        mock_web3.return_value = mock_w3_instance
        mock_w3_instance.HTTPProvider.return_value = MockProvider()
        mock_w3_instance.eth.account.from_key.return_value.address = '0xAdminAddress'
        
        with patch('blockchain.services.BlockchainService.load_contracts'):
            service = BlockchainService()
            
            nombre_rol = "MINTER_ROLE"
            hash_rol = service.get_role_hash(nombre_rol)  # Llamar al método del servicio
            
            # Verificar que keccak fue llamado con el parámetro correcto
            mock_web3.keccak.assert_called_once_with(text=nombre_rol)
            
            # Ahora debería pasar porque devolvemos bytes reales
            self.assertIsInstance(hash_rol, bytes)
            self.assertEqual(hash_rol, hash_esperado)
    
    @patch('blockchain.services.Web3')
    def test_assign_role_success(self, mock_web3):
        """Test para assign_role exitoso - CORREGIDO"""
        # Configurar mocks
        mock_w3_instance = MagicMock()
        mock_web3.return_value = mock_w3_instance
        mock_w3_instance.HTTPProvider.return_value = MockProvider()
        mock_w3_instance.eth.account.from_key.return_value.address = '0xAdminAddress'
        mock_w3_instance.eth.get_transaction_count.return_value = 1
        mock_w3_instance.to_wei.return_value = 100000000000
        
        with patch('blockchain.services.BlockchainService.load_contracts'):
            service = BlockchainService()
            
            # Mock del contrato manualmente
            mock_contract = MagicMock()
            mock_contract.functions.grantRole.return_value.build_transaction.return_value = {
                'nonce': 1, 'gas': 200000, 'gasPrice': 100000000000
            }
            service.registry_contract = mock_contract
            
            # Mock para send_raw_transaction
            mock_w3_instance.eth.send_raw_transaction.return_value.hex.return_value = '0xTxHash'
            
            # Mock para sign_transaction - approach directo
            mock_signed_tx = MagicMock()
            mock_signed_tx.rawTransaction = b'signed_tx_data'
            
            # Mockear directamente el método sign_transaction
            mock_w3_instance.eth.account.sign_transaction = MagicMock(return_value=mock_signed_tx)
            
            result = service.assign_role('0xTargetAddress', 'PRODUCER')
            
            self.assertEqual(result, '0xTxHash')
            mock_contract.functions.grantRole.assert_called_once()
            mock_w3_instance.eth.account.sign_transaction.assert_called_once()
    
    @patch('blockchain.services.Web3')
    def test_has_role_success(self, mock_web3):
        """Test para has_role exitoso"""
        mock_w3_instance = MagicMock()
        mock_web3.return_value = mock_w3_instance
        mock_w3_instance.HTTPProvider.return_value = MockProvider()
        
        with patch('blockchain.services.BlockchainService.load_contracts'):
            service = BlockchainService()
            
            # Mock del contrato manualmente
            mock_contract = MagicMock()
            mock_contract.functions.hasRole.return_value.call.return_value = True
            service.registry_contract = mock_contract
            
            result = service.has_role('0xTargetAddress', 'PRODUCER')
            
            self.assertTrue(result)
            mock_contract.functions.hasRole.assert_called_once()
    
    @patch('blockchain.services.Web3')
    def test_get_balance(self, mock_web3):
        """Test para get_balance"""
        mock_w3_instance = MagicMock()
        mock_web3.return_value = mock_w3_instance
        mock_w3_instance.HTTPProvider.return_value = MockProvider()
        mock_w3_instance.eth.get_balance.return_value = 1000000000000000000  # 1 ETH
        
        with patch('blockchain.services.BlockchainService.load_contracts'):
            service = BlockchainService()
            
            balance = service.get_balance('0xTargetAddress')
            
            self.assertEqual(balance, 1000000000000000000)
            mock_w3_instance.eth.get_balance.assert_called_once()
    
    @patch('blockchain.services.Web3')
    def test_is_valid_wallet(self, mock_web3):
        """Test para is_valid_wallet"""
        mock_w3_instance = MagicMock()
        mock_web3.return_value = mock_w3_instance
        mock_w3_instance.HTTPProvider.return_value = MockProvider()
        mock_w3_instance.is_address.return_value = True
        
        with patch('blockchain.services.BlockchainService.load_contracts'):
            service = BlockchainService()
            
            result = service.is_valid_wallet('0x742d35Cc6634C0532925a3b844Bc454e4438f44e')
            
            self.assertTrue(result)
            mock_w3_instance.is_address.assert_called_once()
    
    @patch('blockchain.services.Web3')
    def test_to_checksum_address(self, mock_web3):
        """Test para to_checksum_address"""
        mock_w3_instance = MagicMock()
        mock_web3.return_value = mock_w3_instance
        mock_w3_instance.HTTPProvider.return_value = MockProvider()
        mock_w3_instance.to_checksum_address.return_value = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        
        with patch('blockchain.services.BlockchainService.load_contracts'):
            service = BlockchainService()
            
            result = service.to_checksum_address('0x742d35cc6634c0532925a3b844bc454e4438f44e')
            
            self.assertEqual(result, '0x742d35Cc6634C0532925a3b844Bc454e4438f44e')
            mock_w3_instance.to_checksum_address.assert_called_once()


class BlockchainServicesEdgeCasesTests(TestCase):
    """Tests para casos edge de BlockchainService"""
    
    def setUp(self):
        """Configuración inicial"""
        settings.BLOCKCHAIN_RPC_URL = 'https://test.rpc.url'
        settings.ADMIN_PRIVATE_KEY = 'test-private-key-0000000000000000000000000000000000000000000000000000000000000000'
        settings.GANADO_TOKEN_ADDRESS = '0x' + '1' * 40
        settings.ANIMAL_NFT_ADDRESS = '0x' + '2' * 40  
        settings.REGISTRY_ADDRESS = '0x' + '3' * 40
    
    @patch('blockchain.services.Web3')
    def test_assign_role_invalid_wallet(self, mock_web3):
        """Test para assign_role con wallet inválida"""
        mock_w3_instance = MagicMock()
        mock_web3.return_value = mock_w3_instance
        mock_w3_instance.HTTPProvider.return_value = MockProvider()
        mock_w3_instance.is_address.return_value = False
        
        with patch('blockchain.services.BlockchainService.load_contracts'):
            service = BlockchainService()
            
            with self.assertRaises(Exception) as context:
                service.assign_role('invalid-wallet', 'PRODUCER')
            
            self.assertIn('Error asignando rol', str(context.exception))
    
    @patch('blockchain.services.Web3')
    def test_has_role_contract_error(self, mock_web3):
        """Test para has_role cuando el contrato falla"""
        mock_w3_instance = MagicMock()
        mock_web3.return_value = mock_w3_instance
        mock_w3_instance.HTTPProvider.return_value = MockProvider()
        
        with patch('blockchain.services.BlockchainService.load_contracts'):
            service = BlockchainService()
            
            # Mock del contrato que falla
            mock_contract = MagicMock()
            mock_contract.functions.hasRole.return_value.call.side_effect = Exception('Contract error')
            service.registry_contract = mock_contract
            
            with self.assertRaises(Exception) as context:
                service.has_role('0xTargetAddress', 'PRODUCER')
            
            self.assertIn('Error verificando rol', str(context.exception))


class BlockchainServicesIntegrationTests(TestCase):
    """Tests de integración para BlockchainService"""
    
    def setUp(self):
        """Configuración inicial"""
        from django.contrib.auth import get_user_model
        from cattle.models import Animal
        
        User = get_user_model()
        
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass',
            wallet_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        )
        
        # Crear animal de prueba - SOLO CAMPOS EXISTENTES
        self.animal = Animal.objects.create(
            ear_tag='TEST001',
            breed='Angus',
            birth_date='2023-01-01',
            owner=self.user,
            ipfs_hash='QmTestHash123456789',
            weight=500.0,
            health_status='HEALTHY'
        )
        
        # Configurar settings
        settings.BLOCKCHAIN_RPC_URL = 'https://test.rpc.url'
        settings.ADMIN_PRIVATE_KEY = 'test-private-key-0000000000000000000000000000000000000000000000000000000000000000'
        settings.GANADO_TOKEN_ADDRESS = '0x' + '1' * 40
        settings.ANIMAL_NFT_ADDRESS = '0x' + '2' * 40  
        settings.REGISTRY_ADDRESS = '0x' + '3' * 40
    
    @patch('blockchain.services.Web3')
    def test_mint_and_associate_animal_success(self, mock_web3):
        """Test para mint_and_associate_animal exitoso"""
        mock_w3_instance = MagicMock()
        mock_web3.return_value = mock_w3_instance
        mock_w3_instance.HTTPProvider.return_value = MockProvider()
        
        with patch('blockchain.services.BlockchainService.load_contracts'):
            with patch('blockchain.services.BlockchainService.mint_animal_nft') as mock_mint:
                mock_mint.return_value = '0xTxHash123'
                
                service = BlockchainService()
                result = service.mint_and_associate_animal(self.animal)
                
                self.assertTrue(result['success'])
                self.assertEqual(result['tx_hash'], '0xTxHash123')
                self.assertEqual(result['animal_id'], self.animal.id)
                mock_mint.assert_called_once()
    
    @patch('blockchain.services.Web3')
    def test_mint_and_associate_animal_no_ipfs(self, mock_web3):
        """Test para mint_and_associate_animal sin IPFS hash"""
        mock_w3_instance = MagicMock()
        mock_web3.return_value = mock_w3_instance
        mock_w3_instance.HTTPProvider.return_value = MockProvider()
        
        # Animal sin IPFS hash
        self.animal.ipfs_hash = ''
        self.animal.save()
        
        with patch('blockchain.services.BlockchainService.load_contracts'):
            service = BlockchainService()
            result = service.mint_and_associate_animal(self.animal)
            
            self.assertFalse(result['success'])
            self.assertIn('no tiene IPFS hash', result['error'])
    
    @patch('blockchain.services.Web3')
    def test_get_animal_nft_info_no_token(self, mock_web3):
        """Test para get_animal_nft_info cuando el animal no tiene token"""
        mock_w3_instance = MagicMock()
        mock_web3.return_value = mock_w3_instance
        mock_w3_instance.HTTPProvider.return_value = MockProvider()
        
        with patch('blockchain.services.BlockchainService.load_contracts'):
            service = BlockchainService()
            result = service.get_animal_nft_info(self.animal)
            
            self.assertIsNone(result)

class BlockchainServicesExtendedTests(TestCase):
    """Tests extendidos para BlockchainService - para mejorar coverage"""
    
    def setUp(self):
        """Configuración inicial"""
        settings.BLOCKCHAIN_RPC_URL = 'https://test.rpc.url'
        settings.ADMIN_PRIVATE_KEY = '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef'
        settings.GANADO_TOKEN_ADDRESS = '0x' + '1' * 40
        settings.ANIMAL_NFT_ADDRESS = '0x' + '2' * 40  
        settings.REGISTRY_ADDRESS = '0x' + '3' * 40
        
        # Mock básico de Web3
        self.mock_w3 = MagicMock()
        self.mock_w3.eth.account.from_key.return_value.address = '0xAdminAddress'
        self.mock_w3.HTTPProvider.return_value = MockProvider()
        self.mock_w3.is_address.return_value = True
        self.mock_w3.to_checksum_address.return_value = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        self.mock_w3.eth.get_balance.return_value = 1000000000000000000
        self.mock_w3.eth.get_transaction_count.return_value = 1
        self.mock_w3.to_wei.return_value = 100000000000
        
    @patch('blockchain.services.Web3')
    @patch('blockchain.services.BlockchainService.load_contracts')
    def test_get_token_balance(self, mock_load_contracts, mock_web3):
        """Test para get_token_balance"""
        mock_web3.return_value = self.mock_w3
        
        service = BlockchainService()
        
        # Mock del contrato de token
        mock_contract = MagicMock()
        mock_contract.functions.balanceOf.return_value.call.return_value = 1000
        service.token_contract = mock_contract
        
        balance = service.get_token_balance('0xTargetAddress')
        
        self.assertEqual(balance, 1000)
        mock_contract.functions.balanceOf.assert_called_once()
    
    @patch('blockchain.services.Web3')
    @patch('blockchain.services.BlockchainService.load_contracts')
    def test_get_nft_owner(self, mock_load_contracts, mock_web3):
        """Test para get_nft_owner"""
        mock_web3.return_value = self.mock_w3
        
        service = BlockchainService()
        
        # Mock del contrato NFT
        mock_contract = MagicMock()
        mock_contract.functions.ownerOf.return_value.call.return_value = '0xOwnerAddress'
        service.nft_contract = mock_contract
        
        owner = service.get_nft_owner(123)
        
        self.assertEqual(owner, '0xOwnerAddress')
        mock_contract.functions.ownerOf.assert_called_once_with(123)
    
    @patch('blockchain.services.Web3')
    @patch('blockchain.services.BlockchainService.load_contracts')
    def test_register_animal_on_chain(self, mock_load_contracts, mock_web3):
        """Test para register_animal_on_chain"""
        mock_web3.return_value = self.mock_w3
        
        service = BlockchainService()
        
        # Mock del contrato registry
        mock_contract = MagicMock()
        mock_contract.functions.registerAnimal.return_value.build_transaction.return_value = {
            'nonce': 1, 'gas': 250000, 'gasPrice': 100000000000
        }
        service.registry_contract = mock_contract
        
        # Mock para send_raw_transaction
        self.mock_w3.eth.send_raw_transaction.return_value.hex.return_value = '0xTxHash'
        
        result = service.register_animal_on_chain(1, 'test_metadata')
        
        self.assertEqual(result, '0xTxHash')
        mock_contract.functions.registerAnimal.assert_called_once()
    
    @patch('blockchain.services.Web3')
    @patch('blockchain.services.BlockchainService.load_contracts')
    def test_is_valid_wallet(self, mock_load_contracts, mock_web3):
        """Test para is_valid_wallet"""
        mock_web3.return_value = self.mock_w3
        
        service = BlockchainService()
        
        result = service.is_valid_wallet('0x742d35Cc6634C0532925a3b844Bc454e4438f44e')
        
        self.assertTrue(result)
        self.mock_w3.is_address.assert_called_once()
    
    @patch('blockchain.services.Web3')
    @patch('blockchain.services.BlockchainService.load_contracts')
    def test_to_checksum_address(self, mock_load_contracts, mock_web3):
        """Test para to_checksum_address"""
        mock_web3.return_value = self.mock_w3
        
        service = BlockchainService()
        
        result = service.to_checksum_address('0x742d35cc6634c0532925a3b844bc454e4438f44e')
        
        self.assertEqual(result, '0x742d35Cc6634C0532925a3b844Bc454e4438f44e')
        self.mock_w3.to_checksum_address.assert_called_once()
    
    @patch('blockchain.services.Web3')
    @patch('blockchain.services.BlockchainService.load_contracts')
    def test_mint_tokens(self, mock_load_contracts, mock_web3):
        """Test para mint_tokens"""
        mock_web3.return_value = self.mock_w3
        
        service = BlockchainService()
        
        # Mock del contrato de token
        mock_contract = MagicMock()
        mock_contract.functions.mint.return_value.build_transaction.return_value = {
            'nonce': 1, 'gas': 200000, 'gasPrice': 100000000000
        }
        service.token_contract = mock_contract
        
        # Mock para send_raw_transaction
        self.mock_w3.eth.send_raw_transaction.return_value.hex.return_value = '0xTokenTxHash'
        
        result = service.mint_tokens('0xTargetAddress', 1000)
        
        self.assertEqual(result, '0xTokenTxHash')
        mock_contract.functions.mint.assert_called_once()

class BlockchainServicesEdgeCasesExtendedTests(TestCase):
    """Tests de edge cases extendidos para BlockchainService"""
    
    def setUp(self):
        """Configuración inicial"""
        settings.BLOCKCHAIN_RPC_URL = 'https://test.rpc.url'
        settings.ADMIN_PRIVATE_KEY = '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef'
        settings.GANADO_TOKEN_ADDRESS = '0x' + '1' * 40
        settings.ANIMAL_NFT_ADDRESS = '0x' + '2' * 40  
        settings.REGISTRY_ADDRESS = '0x' + '3' * 40
    
    @patch('blockchain.services.Web3')
    @patch('blockchain.services.BlockchainService.load_contracts')
    def test_get_nft_owner_error(self, mock_load_contracts, mock_web3):
        """Test para get_nft_owner cuando falla"""
        mock_w3_instance = MagicMock()
        mock_web3.return_value = mock_w3_instance
        mock_w3_instance.HTTPProvider.return_value = MockProvider()
        
        service = BlockchainService()
        
        # Mock del contrato que falla
        mock_contract = MagicMock()
        mock_contract.functions.ownerOf.return_value.call.side_effect = Exception('Contract error')
        service.nft_contract = mock_contract
        
        with self.assertRaises(Exception) as context:
            service.get_nft_owner(123)
        
        self.assertIn('Error obteniendo owner NFT', str(context.exception))
    
    @patch('blockchain.services.Web3')
    @patch('blockchain.services.BlockchainService.load_contracts')
    def test_get_token_balance_error(self, mock_load_contracts, mock_web3):
        """Test para get_token_balance cuando falla"""
        mock_w3_instance = MagicMock()
        mock_web3.return_value = mock_w3_instance
        mock_w3_instance.HTTPProvider.return_value = MockProvider()
        
        service = BlockchainService()
        
        # Mock del contrato que falla
        mock_contract = MagicMock()
        mock_contract.functions.balanceOf.return_value.call.side_effect = Exception('Contract error')
        service.token_contract = mock_contract
        
        with self.assertRaises(Exception) as context:
            service.get_token_balance('0xTargetAddress')
        
        self.assertIn('Error obteniendo balance de tokens', str(context.exception))

class BlockchainServicesComplexTests(TestCase):
    """Tests para métodos complejos de BlockchainService"""
    
    def setUp(self):
        """Configuración inicial con mocks más completos"""
        from django.contrib.auth import get_user_model
        from cattle.models import Animal
        
        User = get_user_model()
        
        # Configurar settings
        settings.BLOCKCHAIN_RPC_URL = 'https://test.rpc.url'
        settings.ADMIN_PRIVATE_KEY = '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef'
        settings.GANADO_TOKEN_ADDRESS = '0x' + '1' * 40
        settings.ANIMAL_NFT_ADDRESS = '0x' + '2' * 40  
        settings.REGISTRY_ADDRESS = '0x' + '3' * 40
        
        # Crear usuario y animal de prueba
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass',
            wallet_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        )
        
        self.animal = Animal.objects.create(
            ear_tag='TEST001',
            breed='Angus',
            birth_date='2023-01-01',
            owner=self.user,
            ipfs_hash='QmTestHash123456789',
            weight=500.0,
            health_status='HEALTHY'
        )
        
        # Mocks básicos
        self.mock_w3 = MagicMock()
        self.mock_w3.eth.account.from_key.return_value.address = '0xAdminAddress'
        self.mock_w3.HTTPProvider.return_value = MockProvider()
        self.mock_w3.is_address.return_value = True
        self.mock_w3.to_checksum_address.return_value = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        self.mock_w3.eth.get_balance.return_value = 1000000000000000000
        self.mock_w3.eth.get_transaction_count.return_value = 1
        self.mock_w3.to_wei.return_value = 100000000000
        self.mock_w3.eth.send_raw_transaction.return_value.hex.return_value = '0xTxHash'
        self.mock_w3.eth.wait_for_transaction_receipt.return_value = {'status': 1, 'logs': []}
    
    @patch('blockchain.services.Web3')
    @patch('blockchain.services.BlockchainService.load_contracts')
    def test_mint_animal_nft_success(self, mock_load_contracts, mock_web3):
        """Test para mint_animal_nft exitoso"""
        mock_web3.return_value = self.mock_w3
        
        service = BlockchainService()
        
        # Mock del contrato NFT
        mock_contract = MagicMock()
        mock_contract.functions.mintAnimal.return_value.build_transaction.return_value = {
            'nonce': 1, 'gas': 500000, 'gasPrice': 100000000000
        }
        service.nft_contract = mock_contract
        
        result = service.mint_animal_nft(
            '0xOwnerAddress', 
            'ipfs://QmTestHash', 
            'ipfs://QmOperationalHash'
        )
        
        self.assertEqual(result, '0xTxHash')
        mock_contract.functions.mintAnimal.assert_called_once()
    
    @patch('blockchain.services.Web3')
    @patch('blockchain.services.BlockchainService.load_contracts')
    def test_mint_and_associate_animal_success(self, mock_load_contracts, mock_web3):
        """Test para mint_and_associate_animal exitoso"""
        mock_web3.return_value = self.mock_w3
        
        service = BlockchainService()
        
        # Mock del método mint_animal_nft
        with patch.object(service, 'mint_animal_nft', return_value='0xTxHash'):
            result = service.mint_and_associate_animal(self.animal)
            
            self.assertTrue(result['success'])
            self.assertEqual(result['tx_hash'], '0xTxHash')
            self.assertEqual(result['animal_id'], self.animal.id)
    
    @patch('blockchain.services.Web3')
    @patch('blockchain.services.BlockchainService.load_contracts')
    def test_mint_and_associate_animal_no_ipfs(self, mock_load_contracts, mock_web3):
        """Test para mint_and_associate_animal sin IPFS hash"""
        mock_web3.return_value = self.mock_w3
        
        service = BlockchainService()
        
        # Animal sin IPFS hash
        self.animal.ipfs_hash = ''
        self.animal.save()
        
        result = service.mint_and_associate_animal(self.animal)
        
        self.assertFalse(result['success'])
        self.assertIn('no tiene IPFS hash', result['error'])
    
    @patch('blockchain.services.Web3')
    @patch('blockchain.services.BlockchainService.load_contracts')
    def test_get_animal_nft_info(self, mock_load_contracts, mock_web3):
        """Test para get_animal_nft_info"""
        mock_web3.return_value = self.mock_w3
        
        service = BlockchainService()
        
        # Mock del contrato NFT
        mock_contract = MagicMock()
        mock_contract.functions.ownerOf.return_value.call.return_value = '0xOwnerAddress'
        mock_contract.functions.tokenURI.return_value.call.return_value = 'ipfs://QmTestHash'
        service.nft_contract = mock_contract
        
        # Animal con token_id
        self.animal.token_id = 123
        self.animal.nft_owner_wallet = '0xOwnerAddress'
        self.animal.save()
        
        result = service.get_animal_nft_info(self.animal)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['token_id'], 123)
        self.assertEqual(result['owner'], '0xOwnerAddress')
        self.assertEqual(result['token_uri'], 'ipfs://QmTestHash')
    
    @patch('blockchain.services.Web3')
    @patch('blockchain.services.BlockchainService.load_contracts')
    def test_get_animal_nft_info_no_token(self, mock_load_contracts, mock_web3):
        """Test para get_animal_nft_info cuando el animal no tiene token"""
        mock_web3.return_value = self.mock_w3
        
        service = BlockchainService()
        
        # Animal sin token_id
        self.animal.token_id = None
        self.animal.save()
        
        result = service.get_animal_nft_info(self.animal)
        
        self.assertIsNone(result)
    
    @patch('blockchain.services.Web3')
    @patch('blockchain.services.BlockchainService.load_contracts')
    def test_verify_animal_nft(self, mock_load_contracts, mock_web3):
        """Test para verify_animal_nft"""
        mock_web3.return_value = self.mock_w3
        
        service = BlockchainService()
        
        # Mock del contrato NFT
        mock_contract = MagicMock()
        mock_contract.functions.ownerOf.return_value.call.return_value = '0xOwnerAddress'
        mock_contract.functions.tokenURI.return_value.call.return_value = 'ipfs://QmTestHash123456789'
        service.nft_contract = mock_contract
        
        # Animal con token_id y IPFS
        self.animal.token_id = 123
        self.animal.nft_owner_wallet = '0xOwnerAddress'
        self.animal.ipfs_hash = 'QmTestHash123456789'
        self.animal.save()
        
        result = service.verify_animal_nft(self.animal)
        
        self.assertTrue(result['verified'])
        self.assertTrue(result['owner_matches'])
        self.assertTrue(result['ipfs_in_uri'])
    
    @patch('blockchain.services.Web3')
    @patch('blockchain.services.BlockchainService.load_contracts')
    def test_wait_for_transaction(self, mock_load_contracts, mock_web3):
        """Test para wait_for_transaction"""
        mock_web3.return_value = self.mock_w3
        
        service = BlockchainService()
        
        result = service.wait_for_transaction('0xTxHash')
        
        self.assertEqual(result, {'status': 1, 'logs': []})
        self.mock_w3.eth.wait_for_transaction_receipt.assert_called_once()

class BlockchainServicesHealthIoTests(TestCase):
    """Tests para métodos de salud y IoT de BlockchainService"""
    
    def setUp(self):
        """Configuración inicial"""
        from django.contrib.auth import get_user_model
        from cattle.models import Animal
        from iot.models import IoTDevice
        
        User = get_user_model()
        
        # Configurar settings
        settings.BLOCKCHAIN_RPC_URL = 'https://test.rpc.url'
        settings.ADMIN_PRIVATE_KEY = '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef'
        settings.GANADO_TOKEN_ADDRESS = '0x' + '1' * 40
        settings.ANIMAL_NFT_ADDRESS = '0x' + '2' * 40  
        settings.REGISTRY_ADDRESS = '0x' + '3' * 40
        
        # Crear usuario, animal y dispositivo
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass',
            wallet_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        )
        
        self.vet_user = User.objects.create_user(
            username='vetuser',
            email='vet@example.com',
            password='vetpass',
            wallet_address='0xVetAddress1234567890123456789012345678901234'
        )
        
        self.animal = Animal.objects.create(
            ear_tag='TEST001',
            breed='Angus',
            birth_date='2023-01-01',
            owner=self.user,
            ipfs_hash='QmTestHash123456789',
            weight=500.0,
            health_status='HEALTHY',
            token_id=123
        )
        
        self.device = IoTDevice.objects.create(
            device_id='DEV001',
            device_type='TEMPERATURE',
            name='Test Device',
            description='Test IoT Device',
            status='ACTIVE',
            animal=self.animal,
            owner=self.user,
            firmware_version='1.0.0',
            battery_level=90
        )
        
        # Mocks básicos
        self.mock_w3 = MagicMock()
        self.mock_w3.eth.account.from_key.return_value.address = '0xAdminAddress'
        self.mock_w3.HTTPProvider.return_value = MockProvider()
        self.mock_w3.eth.get_transaction_count.return_value = 1
        self.mock_w3.to_wei.return_value = 100000000000
        self.mock_w3.eth.send_raw_transaction.return_value.hex.return_value = '0xHealthTxHash'
    
    @patch('blockchain.services.Web3')
    @patch('blockchain.services.BlockchainService.load_contracts')
    def test_update_animal_health(self, mock_load_contracts, mock_web3):
        """Test para update_animal_health"""
        mock_web3.return_value = self.mock_w3
        
        service = BlockchainService()
        
        # Mock del contrato NFT
        mock_contract = MagicMock()
        mock_contract.functions.updateOperational.return_value.build_transaction.return_value = {
            'nonce': 1, 'gas': 300000, 'gasPrice': 100000000000
        }
        service.nft_contract = mock_contract
        
        result = service.update_animal_health(
            animal_id=self.animal.id,
            health_status='SICK',
            source='VETERINARIAN',
            veterinarian_wallet=self.vet_user.wallet_address,
            notes='Test health update'
        )
        
        self.assertEqual(result, '0xHealthTxHash')
        mock_contract.functions.updateOperational.assert_called_once()
    
    @patch('blockchain.services.Web3')
    @patch('blockchain.services.BlockchainService.load_contracts')
    def test_update_health_from_iot(self, mock_load_contracts, mock_web3):
        """Test para update_health_from_iot"""
        mock_web3.return_value = self.mock_w3
        
        service = BlockchainService()
        
        # Mock del método update_animal_health
        with patch.object(service, 'update_animal_health', return_value='0xIoTHealthTxHash'):
            result = service.update_health_from_iot(
                animal_id=self.animal.id,
                health_status='HEALTHY',
                device_id='DEV001',
                temperature=38.5,
                heart_rate=75
            )
            
            self.assertTrue(result['success'])
            self.assertEqual(result['tx_hash'], '0xIoTHealthTxHash')

class BlockchainServicesTransactionTests(TestCase):
    """Tests para métodos de transacciones e historial"""
    
    def setUp(self):
        """Configuración inicial"""
        from django.contrib.auth import get_user_model
        from cattle.models import Animal
        
        User = get_user_model()
        
        settings.BLOCKCHAIN_RPC_URL = 'https://test.rpc.url'
        settings.ADMIN_PRIVATE_KEY = '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef'
        settings.GANADO_TOKEN_ADDRESS = '0x' + '1' * 40
        settings.ANIMAL_NFT_ADDRESS = '0x' + '2' * 40  
        settings.REGISTRY_ADDRESS = '0x' + '3' * 40
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass',
            wallet_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        )
        
        self.animal = Animal.objects.create(
            ear_tag='TEST001',
            breed='Angus',
            birth_date='2023-01-01',
            owner=self.user,
            ipfs_hash='QmTestHash123456789',
            weight=500.0,
            health_status='HEALTHY',
            token_id=123
        )
        
        self.mock_w3 = MagicMock()
        self.mock_w3.eth.account.from_key.return_value.address = '0xAdminAddress'
        self.mock_w3.HTTPProvider.return_value = MockProvider()
        self.mock_w3.eth.get_transaction_count.return_value = 1
        self.mock_w3.to_wei.return_value = 100000000000
    
    @patch('blockchain.services.Web3')
    @patch('blockchain.services.BlockchainService.load_contracts')
    def test_get_transaction_history(self, mock_load_contracts, mock_web3):
        """Test para get_transaction_history"""
        mock_web3.return_value = self.mock_w3
        
        service = BlockchainService()
        
        # Mock del contrato NFT
        mock_contract = MagicMock()
        mock_contract.events.Transfer.return_value.get_logs.return_value = [
            {
                'args': {'from': '0xFrom', 'to': '0xTo'},
                'blockNumber': 12345,
                'transactionHash': MagicMock(hex=lambda: '0xTxHash123')
            }
        ]
        service.nft_contract = mock_contract
        
        # Mock para get_block
        self.mock_w3.eth.get_block.return_value = {'timestamp': 1234567890}
        
        history = service.get_transaction_history(self.animal.id)
        
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['type'], 'TRANSFER')
        self.assertEqual(history[0]['transaction_hash'], '0xTxHash123')
    
    @patch('blockchain.services.Web3')
    @patch('blockchain.services.BlockchainService.load_contracts')
    def test_get_transaction_history_no_token(self, mock_load_contracts, mock_web3):
        """Test para get_transaction_history sin token_id"""
        mock_web3.return_value = self.mock_w3
        
        service = BlockchainService()
        
        # Animal sin token_id
        self.animal.token_id = None
        self.animal.save()
        
        history = service.get_transaction_history(self.animal.id)
        
        self.assertEqual(history, [])
    
    @patch('blockchain.services.Web3')
    @patch('blockchain.services.BlockchainService.load_contracts')
    def test_get_animal_by_token_id(self, mock_load_contracts, mock_web3):
        """Test para get_animal_by_token_id"""
        mock_web3.return_value = self.mock_w3
        
        service = BlockchainService()
        
        animal = service.get_animal_by_token_id(123)
        
        self.assertEqual(animal, self.animal)
    
    @patch('blockchain.services.Web3')
    @patch('blockchain.services.BlockchainService.load_contracts')
    def test_get_animal_by_token_id_not_found(self, mock_load_contracts, mock_web3):
        """Test para get_animal_by_token_id cuando no existe"""
        mock_web3.return_value = self.mock_w3
        
        service = BlockchainService()
        
        animal = service.get_animal_by_token_id(999)
        
        self.assertIsNone(animal)

class BlockchainServicesEventTests(TestCase):
    """Tests para métodos de procesamiento de eventos"""
    
    def setUp(self):
        """Configuración inicial"""
        settings.BLOCKCHAIN_RPC_URL = 'https://test.rpc.url'
        settings.ADMIN_PRIVATE_KEY = '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef'
        settings.GANADO_TOKEN_ADDRESS = '0x' + '1' * 40
        settings.ANIMAL_NFT_ADDRESS = '0x' + '2' * 40  
        settings.REGISTRY_ADDRESS = '0x' + '3' * 40
        
        self.mock_w3 = MagicMock()
        self.mock_w3.eth.account.from_key.return_value.address = '0xAdminAddress'
        self.mock_w3.HTTPProvider.return_value = MockProvider()
        self.mock_w3.eth.get_transaction_count.return_value = 1
        self.mock_w3.to_wei.return_value = 100000000000
    
    @patch('blockchain.services.Web3')
    @patch('blockchain.services.BlockchainService.load_contracts')
    def test_get_last_token_id(self, mock_load_contracts, mock_web3):
        """Test para _get_last_token_id"""
        mock_web3.return_value = self.mock_w3
        
        service = BlockchainService()
        
        # Mock del contrato NFT
        mock_contract = MagicMock()
        mock_contract.functions.totalSupply.return_value.call.return_value = 100
        service.nft_contract = mock_contract
        
        token_id = service._get_last_token_id()
        
        self.assertEqual(token_id, 100)
    
    @patch('blockchain.services.Web3')
    @patch('blockchain.services.BlockchainService.load_contracts')
    def test_get_last_token_id_error(self, mock_load_contracts, mock_web3):
        """Test para _get_last_token_id cuando falla"""
        mock_web3.return_value = self.mock_w3
        
        service = BlockchainService()
        
        # Mock del contrato NFT que falla
        mock_contract = MagicMock()
        mock_contract.functions.totalSupply.return_value.call.side_effect = Exception('Contract error')
        service.nft_contract = mock_contract
        
        token_id = service._get_last_token_id()
        
        self.assertIsNone(token_id)