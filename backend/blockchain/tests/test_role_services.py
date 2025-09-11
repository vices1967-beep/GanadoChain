from rest_framework.test import APITestCase
from unittest.mock import patch, MagicMock
from web3 import Web3

class RoleServiceTests(APITestCase):
    """Tests para los métodos de roles y permisos en services.py"""
    
    @patch('blockchain.services.logger')
    @patch('blockchain.services.BlockchainService.__init__', return_value=None)
    def test_assign_role_success(self, mock_init, mock_logger):
        """Test para assign_role exitoso"""
        from ..services import BlockchainService
        
        service = BlockchainService()
        service.w3 = MagicMock()
        service.wallet_address = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        service.private_key = 'test_private_key'
        service.registry_contract = MagicMock()
        
        # Mockear las llamadas a blockchain
        service.registry_contract.functions.grantRole.return_value.build_transaction.return_value = {}
        service.w3.eth.account.sign_transaction.return_value.rawTransaction = b'signed_tx'
        service.w3.eth.send_raw_transaction.return_value.hex.return_value = '0xroletx'
        service.w3.eth.get_transaction_count.return_value = 1
        
        # Mockear to_checksum_address
        with patch('web3.Web3.to_checksum_address') as mock_checksum:
            mock_checksum.return_value = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
            
            result = service.assign_role(
                target_wallet='0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
                role_name='PRODUCER_ROLE'
            )
        
        self.assertEqual(result, '0xroletx')
        service.registry_contract.functions.grantRole.assert_called_once()

    @patch('blockchain.services.logger')
    @patch('blockchain.services.BlockchainService.__init__', return_value=None)
    def test_has_role_true(self, mock_init, mock_logger):
        """Test para has_role que devuelve True"""
        from ..services import BlockchainService
        
        service = BlockchainService()
        service.registry_contract = MagicMock()
        service.registry_contract.functions.hasRole.return_value.call.return_value = True
        
        # Mockear to_checksum_address
        with patch('web3.Web3.to_checksum_address') as mock_checksum:
            mock_checksum.return_value = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
            
            result = service.has_role(
                wallet_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
                role_name='PRODUCER_ROLE'
            )
        
        self.assertTrue(result)

    @patch('blockchain.services.logger')
    @patch('blockchain.services.BlockchainService.__init__', return_value=None)
    def test_has_role_false(self, mock_init, mock_logger):
        """Test para has_role que devuelve False"""
        from ..services import BlockchainService
        
        service = BlockchainService()
        service.registry_contract = MagicMock()
        service.registry_contract.functions.hasRole.return_value.call.return_value = False
        
        # Mockear to_checksum_address
        with patch('web3.Web3.to_checksum_address') as mock_checksum:
            mock_checksum.return_value = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
            
            result = service.has_role(
                wallet_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
                role_name='PRODUCER_ROLE'
            )
        
        self.assertFalse(result)

    @patch('blockchain.services.logger')
    @patch('blockchain.services.BlockchainService.__init__', return_value=None)
    def test_get_role_hash(self, mock_init, mock_logger):
        """Test para get_role_hash"""
        from ..services import BlockchainService
        
        service = BlockchainService()
        service.w3 = Web3()
        
        role_hash = service.get_role_hash('PRODUCER_ROLE')
        
        expected_hash = Web3.keccak(text='PRODUCER_ROLE')
        self.assertEqual(role_hash, expected_hash)

if __name__ == '__main__':
    import unittest
    unittest.main()