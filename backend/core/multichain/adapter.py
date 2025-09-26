from abc import ABC, abstractmethod
from django.conf import settings
from web3 import Web3
import json
import requests

class BlockchainAdapter(ABC):
    """Adapter base para diferentes blockchains"""
    
    def __init__(self, network):
        self.network = network
        self.w3 = self._connect_to_network()
    
    @abstractmethod
    def _connect_to_network(self):
        """Conectar a la red blockchain"""
        pass
    
    @abstractmethod
    def mint_nft(self, metadata_uri, to_address):
        """Mintear un NFT"""
        pass
    
    @abstractmethod
    def transfer_nft(self, token_id, to_address):
        """Transferir un NFT"""
        pass
    
    @abstractmethod
    def get_nft_info(self, token_id):
        """Obtener información del NFT"""
        pass

class StarknetAdapter(BlockchainAdapter):
    """Adapter para Starknet"""
    
    def _connect_to_network(self):
        # Conexión a Starknet via RPC
        if self.network.testnet:
            rpc_url = self.network.rpc_url or settings.STARKNET_TESTNET_RPC
        else:
            rpc_url = self.network.rpc_url or settings.STARKNET_MAINNET_RPC
        
        # Usar biblioteca específica para Starknet
        from starknet_py.net.full_node_client import FullNodeClient
        return FullNodeClient(node_url=rpc_url)
    
    def mint_nft(self, metadata_uri, to_address):
        """Mint NFT en Starknet"""
        try:
            # Implementar lógica específica de Starknet
            # Usar contratos compiled con Cairo
            contract_address = self.network.contract_addresses.get('nft_contract')
            
            # Lógica de mint...
            return {
                'success': True,
                'transaction_hash': '0x123...',
                'token_id': 1
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def transfer_nft(self, token_id, to_address):
        # Implementación específica para Starknet
        pass
    
    def get_nft_info(self, token_id):
        # Implementación específica para Starknet
        pass

class PolygonAdapter(BlockchainAdapter):
    """Adapter para Polygon"""
    
    def _connect_to_network(self):
        # Conexión a Polygon via Web3
        if self.network.testnet:
            rpc_url = self.network.rpc_url or settings.POLYGON_TESTNET_RPC
        else:
            rpc_url = self.network.rpc_url or settings.POLYGON_MAINNET_RPC
        
        return Web3(Web3.HTTPProvider(rpc_url))
    
    def mint_nft(self, metadata_uri, to_address):
        """Mint NFT en Polygon"""
        try:
            # Cargar contrato ERC721
            with open('contracts/ERC721.json') as f:
                contract_abi = json.load(f)['abi']
            
            contract = self.w3.eth.contract(
                address=self.network.contract_addresses['nft_contract'],
                abi=contract_abi
            )
            
            # Construir transacción
            transaction = contract.functions.mint(to_address, metadata_uri).build_transaction({
                'from': settings.HOT_WALLET_ADDRESS,
                'nonce': self.w3.eth.get_transaction_count(settings.HOT_WALLET_ADDRESS),
                'gas': 300000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            # Firmar y enviar
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction, 
                private_key=settings.HOT_WALLET_PRIVATE_KEY
            )
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            return {
                'success': True,
                'transaction_hash': tx_hash.hex(),
                'token_id': self._get_next_token_id(contract)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_next_token_id(self, contract):
        """Obtener próximo token ID"""
        return contract.functions.totalSupply().call() + 1
    

class EthereumAdapter(BlockchainAdapter):
    """Adapter para Ethereum (mainnet y testnets)"""
    
    def _connect_to_network(self):
        # Conexión a Ethereum via Web3
        if self.network.testnet:
            rpc_url = self.network.rpc_url or settings.ETHEREUM_TESTNET_RPC
        else:
            rpc_url = self.network.rpc_url or settings.ETHEREUM_MAINNET_RPC
        
        return Web3(Web3.HTTPProvider(rpc_url))
    
    def mint_nft(self, metadata_uri, to_address):
        """Mint NFT en Ethereum"""
        try:
            # Cargar contrato ERC721
            with open('contracts/ERC721.json') as f:
                contract_abi = json.load(f)['abi']
            
            contract = self.w3.eth.contract(
                address=self.network.contract_addresses['nft_contract'],
                abi=contract_abi
            )
            
            # Construir transacción
            transaction = contract.functions.mint(to_address, metadata_uri).build_transaction({
                'from': settings.HOT_WALLET_ADDRESS,
                'nonce': self.w3.eth.get_transaction_count(settings.HOT_WALLET_ADDRESS),
                'gas': 300000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            # Firmar y enviar
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction, 
                private_key=settings.HOT_WALLET_PRIVATE_KEY
            )
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            return {
                'success': True,
                'transaction_hash': tx_hash.hex(),
                'token_id': self._get_next_token_id(contract)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_next_token_id(self, contract):
        """Obtener próximo token ID"""
        return contract.functions.totalSupply().call() + 1
    
    def transfer_nft(self, token_id, to_address):
        """Transferir NFT en Ethereum"""
        try:
            # Cargar contrato ERC721
            with open('contracts/ERC721.json') as f:
                contract_abi = json.load(f)['abi']
            
            contract = self.w3.eth.contract(
                address=self.network.contract_addresses['nft_contract'],
                abi=contract_abi
            )
            
            # Construir transacción
            transaction = contract.functions.transferFrom(
                settings.HOT_WALLET_ADDRESS,
                to_address,
                token_id
            ).build_transaction({
                'from': settings.HOT_WALLET_ADDRESS,
                'nonce': self.w3.eth.get_transaction_count(settings.HOT_WALLET_ADDRESS),
                'gas': 300000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            # Firmar y enviar
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction, 
                private_key=settings.HOT_WALLET_PRIVATE_KEY
            )
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            return {
                'success': True,
                'transaction_hash': tx_hash.hex()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_nft_info(self, token_id):
        """Obtener información del NFT en Ethereum"""
        try:
            # Cargar contrato ERC721
            with open('contracts/ERC721.json') as f:
                contract_abi = json.load(f)['abi']
            
            contract = self.w3.eth.contract(
                address=self.network.contract_addresses['nft_contract'],
                abi=contract_abi
            )
            
            # Obtener datos del NFT
            owner = contract.functions.ownerOf(token_id).call()
            token_uri = contract.functions.tokenURI(token_id).call()
            
            return {
                'success': True,
                'owner': owner,
                'token_uri': token_uri
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

class BlockchainAdapterFactory:
    """Factory para crear adapters específicos"""
    
    @staticmethod
    def get_adapter(network):
        if network.name.upper() == 'STARKNET':
            return StarknetAdapter(network)
        elif network.name.upper() == 'POLYGON':
            return PolygonAdapter(network)
        elif network.name.upper() == 'ETHEREUM':
            return EthereumAdapter(network)  # Implementar similar a Polygon
        else:
            raise ValueError(f"Unsupported network: {network.name}")