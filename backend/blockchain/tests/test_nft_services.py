from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from cattle.models import Animal
from cattle.models import HealthStatus
import json

User = get_user_model()

class NFTServiceTests(APITestCase):
    """Tests para los métodos de NFT en services.py"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='producer',
            email='producer@example.com',
            password='testpass123',
            wallet_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e',  # ← Dirección válida
            role='PRODUCER_ROLE'
        )
        
        self.animal = Animal.objects.create(
            ear_tag='NFT001',
            breed='Angus',
            birth_date='2023-01-01',
            weight=500.00,
            health_status='HEALTHY',
            location='Test Farm',
            owner=self.user,
            ipfs_hash='QmTestHash123'
        )

    @patch('blockchain.services.logger')
    @patch('blockchain.services.BlockchainService.__init__', return_value=None)
    def test_mint_animal_nft_success(self, mock_init, mock_logger):
        """Test para mint_animal_nft exitoso"""
        from ..services import BlockchainService
        
        service = BlockchainService()
        service.w3 = MagicMock()
        service.wallet_address = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'  # ← Dirección válida
        service.private_key = 'test_private_key'
        service.nft_contract = MagicMock()
        
        # Mockear las llamadas a blockchain
        service.nft_contract.functions.mintAnimal.return_value.build_transaction.return_value = {}
        service.w3.eth.account.sign_transaction.return_value.rawTransaction = b'signed_tx'
        service.w3.eth.send_raw_transaction.return_value.hex.return_value = '0xnfttx'
        service.w3.eth.get_transaction_count.return_value = 1
        
        # Mockear to_checksum_address para evitar errores
        with patch('web3.Web3.to_checksum_address') as mock_checksum:
            mock_checksum.return_value = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
            
            result = service.mint_animal_nft(
                owner_wallet='0x742d35Cc6634C0532925a3b844Bc454e4438f44e',  # ← Dirección válida
                metadata_uri='ipfs://QmTestHash123',
                operational_ipfs='ipfs://QmOperationalHash'
            )
        
        self.assertEqual(result, '0xnfttx')
        service.nft_contract.functions.mintAnimal.assert_called_once()

    @patch('blockchain.services.logger')
    @patch('blockchain.services.BlockchainService.__init__', return_value=None)
    def test_mint_animal_nft_exception(self, mock_init, mock_logger):
        """Test para mint_animal_nft con excepción"""
        from ..services import BlockchainService
        
        service = BlockchainService()
        service.w3 = MagicMock()
        service.wallet_address = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        service.private_key = 'test_private_key'
        service.nft_contract = MagicMock()
        
        # Mockear excepción
        service.nft_contract.functions.mintAnimal.side_effect = Exception('Blockchain error')
        
        with patch('web3.Web3.to_checksum_address') as mock_checksum:
            mock_checksum.return_value = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
            
            with self.assertRaises(Exception) as context:
                service.mint_animal_nft(
                    owner_wallet='0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
                    metadata_uri='ipfs://QmTestHash123'
                )
        
        self.assertIn('Error minting NFT', str(context.exception))

    @patch('blockchain.services.logger')
    @patch('blockchain.services.BlockchainService.__init__', return_value=None)
    def test_mint_and_associate_animal_success(self, mock_init, mock_logger):
        """Test para mint_and_associate_animal exitoso"""
        from ..services import BlockchainService
        
        service = BlockchainService()
        service.mint_animal_nft = MagicMock(return_value='0xminttx')
        
        result = service.mint_and_associate_animal(
            animal=self.animal,
            owner_wallet='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['tx_hash'], '0xminttx')
        self.assertEqual(result['animal_id'], self.animal.id)

    @patch('blockchain.services.logger')
    @patch('blockchain.services.BlockchainService.__init__', return_value=None)
    def test_mint_and_associate_animal_no_ipfs(self, mock_init, mock_logger):
        """Test para mint_and_associate_animal sin IPFS hash"""
        from ..services import BlockchainService
        
        service = BlockchainService()
        self.animal.ipfs_hash = ''
        self.animal.save()
        
        result = service.mint_and_associate_animal(
            animal=self.animal,
            owner_wallet='0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        )
        
        self.assertFalse(result['success'])
        self.assertIn('IPFS hash', result['error'])

    @patch('blockchain.services.logger')
    @patch('blockchain.services.BlockchainService.__init__', return_value=None)
    def test_get_nft_owner(self, mock_init, mock_logger):
        """Test para get_nft_owner"""
        from ..services import BlockchainService
        
        service = BlockchainService()
        service.nft_contract = MagicMock()
        service.nft_contract.functions.ownerOf.return_value.call.return_value = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        
        owner = service.get_nft_owner(123)
        
        self.assertEqual(owner, '0x742d35Cc6634C0532925a3b844Bc454e4438f44e')
        service.nft_contract.functions.ownerOf.assert_called_with(123)

if __name__ == '__main__':
    import unittest
    unittest.main()