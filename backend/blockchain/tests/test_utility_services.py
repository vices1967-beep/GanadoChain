from rest_framework.test import APITestCase
from unittest.mock import patch, MagicMock
from cattle.models import Animal, HealthStatus
from django.contrib.auth import get_user_model

User = get_user_model()

class UtilityServiceTests(APITestCase):
    """Tests para métodos utilitarios en services.py"""
    
    def setUp(self):
        # Crear usuario para las pruebas
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            wallet_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        )
        
        # Crear animal para las pruebas
        self.animal = Animal.objects.create(
            ear_tag='TEST_ANIMAL',
            breed='Test Breed',
            birth_date='2023-01-01',
            weight=400.00,
            health_status=HealthStatus.HEALTHY,
            location='Test Farm',
            owner=self.user,
            ipfs_hash='QmTestHash',
            token_id=999
        )
    
    @patch('blockchain.services.logger')
    @patch('blockchain.services.BlockchainService.__init__', return_value=None)
    def test_wait_for_transaction(self, mock_init, mock_logger):
        """Test para wait_for_transaction"""
        from ..services import BlockchainService
        
        service = BlockchainService()
        service.w3 = MagicMock()
        service.w3.eth.wait_for_transaction_receipt.return_value = {'status': 1}
        
        result = service.wait_for_transaction('0xtxhash')
        
        self.assertEqual(result, {'status': 1})
        service.w3.eth.wait_for_transaction_receipt.assert_called_with('0xtxhash', timeout=120)

    @patch('blockchain.services.logger')
    @patch('blockchain.services.BlockchainService.__init__', return_value=None)
    def test_wait_for_transaction_custom_timeout(self, mock_init, mock_logger):
        """Test para wait_for_transaction con timeout personalizado"""
        from ..services import BlockchainService
        
        service = BlockchainService()
        service.w3 = MagicMock()
        service.w3.eth.wait_for_transaction_receipt.return_value = {'status': 1}
        
        result = service.wait_for_transaction('0xtxhash', timeout=60)
        
        self.assertEqual(result, {'status': 1})
        service.w3.eth.wait_for_transaction_receipt.assert_called_with('0xtxhash', timeout=60)

@patch('blockchain.services.logger')
@patch('blockchain.services.BlockchainService.__init__', return_value=None)
def test_get_transaction_history(self, mock_init, mock_logger):
    """Test para get_transaction_history"""
    from ..services import BlockchainService
    
    service = BlockchainService()
    service.w3 = MagicMock()
    service.nft_contract = MagicMock()
    
    # Mockear eventos de transferencia CORRECTAMENTE
    # Crear un mock que se parezca a un evento real de web3.py
    mock_event = {
        'args': {
            'from': '0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
            'to': '0x0000000000000000000000000000000000000000',
            'tokenId': 999  # ← AÑADIR tokenId que coincida con el animal
        },
        'blockNumber': 1000000,
        'transactionHash': MagicMock()
    }
    mock_event['transactionHash'].hex.return_value = '0xtransfertx'
    
    # Mockear correctamente la llamada a get_logs
    service.nft_contract.events.Transfer.return_value.get_logs.return_value = [mock_event]
    service.w3.eth.get_block.return_value = {'timestamp': 1234567890}
    
    # Usar el animal del setUp (que tiene token_id=999)
    result = service.get_transaction_history(self.animal)
    
    self.assertEqual(len(result), 1)
    self.assertEqual(result[0]['type'], 'TRANSFER')
    self.assertEqual(result[0]['from'], '0x742d35Cc6634C0532925a3b844Bc454e4438f44e')

    @patch('blockchain.services.logger')
    @patch('blockchain.services.BlockchainService.__init__', return_value=None)
    def test_get_transaction_history_no_token_id(self, mock_init, mock_logger):
        """Test para get_transaction_history sin token_id"""
        from ..services import BlockchainService
        
        service = BlockchainService()
        
        # Crear animal sin token_id
        animal_no_token = Animal.objects.create(
            ear_tag='NO_TOKEN_ANIMAL',
            breed='Test Breed',
            birth_date='2023-01-01',
            weight=400.00,
            health_status=HealthStatus.HEALTHY,
            location='Test Farm',
            owner=self.user,
            ipfs_hash='QmTestHashNoToken'
            # Sin token_id
        )
        
        result = service.get_transaction_history(animal_no_token)
        
        self.assertEqual(result, [])

    @patch('blockchain.services.logger')
    @patch('blockchain.services.BlockchainService.__init__', return_value=None)
    def test_get_transaction_history_no_token_id(self, mock_init, mock_logger):
        """Test para get_transaction_history sin token_id"""
        from ..services import BlockchainService
        
        service = BlockchainService()
        
        # Crear animal sin token_id
        animal_no_token = Animal.objects.create(
            ear_tag='NO_TOKEN_ANIMAL',
            breed='Test Breed',
            birth_date='2023-01-01',
            weight=400.00,
            health_status=HealthStatus.HEALTHY,
            location='Test Farm',
            owner=self.user,
            ipfs_hash='QmTestHashNoToken'
            # Sin token_id
        )
        
        result = service.get_transaction_history(animal_no_token)
        
        self.assertEqual(result, [])

if __name__ == '__main__':
    import unittest
    unittest.main()