from rest_framework.test import APITestCase
from unittest.mock import patch, MagicMock

class TokenServiceTests(APITestCase):
    """Tests para los métodos de tokens y balances en services.py"""
    
    @patch('blockchain.services.logger')
    @patch('blockchain.services.BlockchainService.__init__', return_value=None)
    def test_mint_tokens_success(self, mock_init, mock_logger):
        """Test para mint_tokens exitoso"""
        from ..services import BlockchainService
        
        service = BlockchainService()
        service.w3 = MagicMock()
        service.wallet_address = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        service.private_key = 'test_private_key'
        service.token_contract = MagicMock()
        
        # Mockear las llamadas a blockchain
        service.token_contract.functions.mint.return_value.build_transaction.return_value = {}
        service.w3.eth.account.sign_transaction.return_value.rawTransaction = b'signed_tx'
        service.w3.eth.send_raw_transaction.return_value.hex.return_value = '0xtokentx'
        service.w3.eth.get_transaction_count.return_value = 1
        
        # Mockear to_checksum_address
        with patch('web3.Web3.to_checksum_address') as mock_checksum:
            mock_checksum.return_value = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
            
            result = service.mint_tokens(
                to_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
                amount=1000
            )
        
        self.assertEqual(result, '0xtokentx')
        service.token_contract.functions.mint.assert_called_with('0x742d35Cc6634C0532925a3b844Bc454e4438f44e', 1000)

    @patch('blockchain.services.logger')
    @patch('blockchain.services.BlockchainService.__init__', return_value=None)
    def test_mint_tokens_string_amount(self, mock_init, mock_logger):
        """Test para mint_tokens con amount como string"""
        from ..services import BlockchainService
        
        service = BlockchainService()
        service.w3 = MagicMock()
        service.wallet_address = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        service.private_key = 'test_private_key'
        service.token_contract = MagicMock()
        
        # Mockear las llamadas a blockchain
        service.token_contract.functions.mint.return_value.build_transaction.return_value = {}
        service.w3.eth.account.sign_transaction.return_value.rawTransaction = b'signed_tx'
        service.w3.eth.send_raw_transaction.return_value.hex.return_value = '0xtokentx'
        service.w3.eth.get_transaction_count.return_value = 1
        
        # Mockear to_checksum_address
        with patch('web3.Web3.to_checksum_address') as mock_checksum:
            mock_checksum.return_value = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
            
            result = service.mint_tokens(
                to_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
                amount='500'
            )
        
        self.assertEqual(result, '0xtokentx')
        service.token_contract.functions.mint.assert_called_with('0x742d35Cc6634C0532925a3b844Bc454e4438f44e', 500)

    @patch('blockchain.services.logger')
    @patch('blockchain.services.BlockchainService.__init__', return_value=None)
    def test_get_token_balance(self, mock_init, mock_logger):
        """Test para get_token_balance"""
        from ..services import BlockchainService
        
        service = BlockchainService()
        service.token_contract = MagicMock()
        service.token_contract.functions.balanceOf.return_value.call.return_value = 1500
        
        # Mockear to_checksum_address
        with patch('web3.Web3.to_checksum_address') as mock_checksum:
            mock_checksum.return_value = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
            
            balance = service.get_token_balance('0x742d35Cc6634C0532925a3b844Bc454e4438f44e')
        
        self.assertEqual(balance, 1500)
        service.token_contract.functions.balanceOf.assert_called_with('0x742d35Cc6634C0532925a3b844Bc454e4438f44e')

    @patch('blockchain.services.logger')
    @patch('blockchain.services.BlockchainService.__init__', return_value=None)
    def test_get_balance_matic(self, mock_init, mock_logger):
        """Test para get_balance de MATIC"""
        from ..services import BlockchainService
        
        service = BlockchainService()
        service.w3 = MagicMock()
        service.w3.eth.get_balance.return_value = 1000000000000000000  # 1 MATIC en wei
        
        # Mockear to_checksum_address
        with patch('web3.Web3.to_checksum_address') as mock_checksum:
            mock_checksum.return_value = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
            
            balance = service.get_balance('0x742d35Cc6634C0532925a3b844Bc454e4438f44e')
        
        self.assertEqual(balance, 1000000000000000000)
        service.w3.eth.get_balance.assert_called_with('0x742d35Cc6634C0532925a3b844Bc454e4438f44e')

    @patch('blockchain.services.logger')
    @patch('blockchain.services.BlockchainService.__init__', return_value=None)
    def test_get_balance_default_wallet(self, mock_init, mock_logger):
        """Test para get_balance con wallet por defecto"""
        from ..services import BlockchainService
        
        service = BlockchainService()
        service.wallet_address = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        service.w3 = MagicMock()
        service.w3.eth.get_balance.return_value = 500000000000000000  # 0.5 MATIC en wei
        
        # Mockear to_checksum_address
        with patch('web3.Web3.to_checksum_address') as mock_checksum:
            mock_checksum.return_value = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
            
            balance = service.get_balance()
        
        self.assertEqual(balance, 500000000000000000)
        service.w3.eth.get_balance.assert_called_with('0x742d35Cc6634C0532925a3b844Bc454e4438f44e')

    @patch('blockchain.services.logger')
    @patch('blockchain.services.BlockchainService.__init__', return_value=None)
    def test_is_valid_wallet_true(self, mock_init, mock_logger):
        """Test para is_valid_wallet con dirección válida"""
        from ..services import BlockchainService
        
        service = BlockchainService()
        service.w3 = MagicMock()
        service.w3.is_address.return_value = True
        
        result = service.is_valid_wallet('0x742d35Cc6634C0532925a3b844Bc454e4438f44e')
        
        self.assertTrue(result)

    @patch('blockchain.services.logger')
    @patch('blockchain.services.BlockchainService.__init__', return_value=None)
    def test_is_valid_wallet_false(self, mock_init, mock_logger):
        """Test para is_valid_wallet con dirección inválida"""
        from ..services import BlockchainService
        
        service = BlockchainService()
        service.w3 = MagicMock()
        service.w3.is_address.return_value = False
        
        result = service.is_valid_wallet('invalid_address')
        
        self.assertFalse(result)

    @patch('blockchain.services.logger')
    @patch('blockchain.services.BlockchainService.__init__', return_value=None)
    def test_to_checksum_address(self, mock_init, mock_logger):
        """Test para to_checksum_address"""
        from ..services import BlockchainService
        
        service = BlockchainService()
        service.w3 = MagicMock()
        service.w3.to_checksum_address.return_value = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        
        result = service.to_checksum_address('0x742d35cc6634c0532925a3b844bc454e4438f44e')
        
        self.assertEqual(result, '0x742d35Cc6634C0532925a3b844Bc454e4438f44e')

if __name__ == '__main__':
    import unittest
    unittest.main()