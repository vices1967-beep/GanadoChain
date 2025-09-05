from unittest.mock import Mock

class MockBlockchainService:
    def __init__(self):
        # Mock de todas las métodos del servicio
        self.mint_and_associate_animal = Mock()
        self.assign_role = Mock()
        self.has_role = Mock()
        self.mint_tokens = Mock()
        self.update_animal_health = Mock()
        self.get_balance = Mock()
        self.get_animal_history = Mock()
        self.get_animal_nft_info = Mock()
        self.verify_animal_nft = Mock()
        self.get_transaction_history = Mock()
        self.is_valid_wallet = Mock()
        self.to_checksum_address = Mock()
        self.wait_for_transaction = Mock()
        self.call_contract = Mock()
        self.subscribe_to_event = Mock()
        
        # Mock de web3
        self.w3 = Mock()
        self.w3.eth = Mock()
        self.w3.eth.block_number = 1000000
        self.w3.eth.gas_price = 1000000000
        self.w3.eth.chain_id = 80002
        self.wallet_address = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        
        # Configurar valores por defecto para los mocks
        self.mint_and_associate_animal.return_value = {
            'success': True,
            'token_id': 1,
            'tx_hash': '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef',
            'animal_id': 1,
            'ear_tag': 'TEST001',
            'owner_wallet': '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        }
        
        self.assign_role.return_value = '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef'
        self.has_role.return_value = True
        self.mint_tokens.return_value = '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef'
        self.update_animal_health.return_value = '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef'
        self.get_balance.return_value = 1000000000000000000
        self.get_animal_history.return_value = []
        self.get_animal_nft_info.return_value = {
            'token_id': 1,
            'owner': '0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
            'token_uri': 'ipfs://QmTestHash',
            'is_owner_correct': True
        }
        self.verify_animal_nft.return_value = {
            'verified': True,
            'owner_matches': True,
            'ipfs_in_uri': True
        }
        self.get_transaction_history.return_value = []
        self.is_valid_wallet.return_value = True
        self.to_checksum_address.side_effect = lambda x: x.lower()
        self.wait_for_transaction.return_value = {
            'blockNumber': 1000000,
            'status': 1,
            'gasUsed': 21000
        }
        self.call_contract.return_value = {
            'success': True,
            'tx_hash': '0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef'
        }
        self.subscribe_to_event.return_value = {
            'success': True,
            'subscription_id': 'test-subscription-123'
        }
        
        # Configurar métodos de conversión
        self.w3.from_wei = lambda x, unit: x / 10**9 if unit == 'gwei' else x / 10**18
        self.w3.to_wei = lambda x, unit: int(x * 10**9) if unit == 'gwei' else int(x * 10**18)
        self.w3.to_checksum_address = lambda x: x.lower()

# Instancia global del mock
mock_blockchain_service = MockBlockchainService()