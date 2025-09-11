# blockchain/tests/test_batch_services.py
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from cattle.models import Animal, Batch
from cattle.models import HealthStatus
import logging

User = get_user_model()

class BatchServicesTests(APITestCase):
    """Tests para los métodos de batch en services.py"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='producer',
            email='producer@example.com',
            password='testpass123',
            wallet_address='0xProducerAddress12345678901234567890123456',
            role='PRODUCER_ROLE'
        )
        
        # Crear animales para el batch
        self.animal1 = Animal.objects.create(
            ear_tag='BATCH001',
            breed='Angus',
            birth_date='2023-01-01',
            weight=500.00,
            health_status='HEALTHY',
            location='Test Farm',
            owner=self.user,
            ipfs_hash='QmBatchHash1'
        )
        
        self.animal2 = Animal.objects.create(
            ear_tag='BATCH002',
            breed='Hereford',
            birth_date='2023-02-01',
            weight=480.00,
            health_status='HEALTHY', 
            location='Test Farm',
            owner=self.user,
            ipfs_hash='QmBatchHash2'
        )
        
        # Crear batch
        self.batch = Batch.objects.create(
            name='Test Batch',
            origin='Farm A',
            destination='Market B',
            status='CREATED',
            created_by=self.user
        )
        self.batch.animals.add(self.animal1, self.animal2)

    @patch('blockchain.services.logger')
    @patch('blockchain.services.BlockchainService.__init__', return_value=None)
    def test_update_batch_status_success(self, mock_init, mock_logger):
        """Test para update_batch_status exitoso"""
        from ..services import BlockchainService
        
        service = BlockchainService()
        # Mockear TODOS los atributos necesarios
        service.w3 = MagicMock()
        service.wallet_address = '0xTestAddress'
        service.private_key = 'test_private_key'
        service.registry_contract = MagicMock()
        
        # Mockear las llamadas a blockchain de manera más completa
        # 1. Mockear build_transaction
        mock_build_tx = MagicMock()
        service.registry_contract.functions.updateBatchStatus.return_value.build_transaction.return_value = mock_build_tx
        
        # 2. Mockear sign_transaction
        mock_signed_tx = MagicMock()
        mock_signed_tx.rawTransaction = b'signed_tx'
        service.w3.eth.account.sign_transaction.return_value = mock_signed_tx
        
        # 3. Mockear send_raw_transaction
        mock_tx_hash = MagicMock()
        mock_tx_hash.hex.return_value = '0xbatchtx'
        service.w3.eth.send_raw_transaction.return_value = mock_tx_hash
        
        # 4. Mockear wait_for_transaction_receipt para devolver un receipt exitoso
        mock_receipt = MagicMock()
        mock_receipt.status = 1  # Transacción exitosa
        mock_receipt.blockNumber = 1000000
        service.w3.eth.wait_for_transaction_receipt.return_value = mock_receipt
        
        # Asignar blockchain_id al batch
        self.batch.blockchain_id = 123
        self.batch.save()
        
        result = service.update_batch_status(
            batch=self.batch,
            new_status='IN_TRANSIT',
            notes='Batch en camino al mercado'
        )
        
        print("RESULT:", result)  # Para debug
        self.assertTrue(result['success'])
        self.assertEqual(result['tx_hash'], '0xbatchtx')
        service.registry_contract.functions.updateBatchStatus.assert_called_once()
        mock_logger.info.assert_called()

    @patch('blockchain.services.logger')
    @patch('blockchain.services.BlockchainService.__init__', return_value=None)
    def test_update_batch_status_no_blockchain_id(self, mock_init, mock_logger):
        """Test para update_batch_status sin blockchain_id"""
        from ..services import BlockchainService
        
        service = BlockchainService()
        service.w3 = MagicMock()
        service.registry_contract = MagicMock()
        
        # Batch sin blockchain_id
        self.batch.blockchain_id = None
        self.batch.save()
        
        result = service.update_batch_status(
            batch=self.batch,
            new_status='IN_TRANSIT'
        )
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        service.registry_contract.functions.updateBatchStatus.assert_not_called()
        mock_logger.warning.assert_called()

    @patch('blockchain.services.logger')
    @patch('blockchain.services.BlockchainService.__init__', return_value=None)
    def test_update_batch_status_transaction_failed(self, mock_init, mock_logger):
        """Test para update_batch_status cuando falla la transacción"""
        from ..services import BlockchainService
        
        service = BlockchainService()
        service.w3 = MagicMock()
        service.wallet_address = '0xTestAddress'
        service.private_key = 'test_private_key'
        service.registry_contract = MagicMock()
        
        # Mockear transacción fallida
        service.registry_contract.functions.updateBatchStatus.return_value.build_transaction.return_value = {}
        service.w3.eth.account.sign_transaction.return_value.rawTransaction = b'signed_tx'
        service.w3.eth.send_raw_transaction.return_value.hex.return_value = '0xbatchtx'
        service.wait_for_transaction = MagicMock(return_value={'status': 0})  # Transacción fallida
        
        self.batch.blockchain_id = 123
        self.batch.save()
        
        result = service.update_batch_status(
            batch=self.batch,
            new_status='IN_TRANSIT'
        )
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        mock_logger.error.assert_called()

    @patch('blockchain.services.logger')
    @patch('blockchain.services.BlockchainService.__init__', return_value=None)
    def test_update_batch_status_exception(self, mock_init, mock_logger):
        """Test para update_batch_status con excepción"""
        from ..services import BlockchainService
        
        service = BlockchainService()
        service.w3 = MagicMock()
        service.wallet_address = '0xTestAddress'
        service.private_key = 'test_private_key'
        service.registry_contract = MagicMock()
        
        # Mockear excepción
        service.registry_contract.functions.updateBatchStatus.side_effect = Exception('Error de blockchain')
        
        self.batch.blockchain_id = 123
        self.batch.save()
        
        result = service.update_batch_status(
            batch=self.batch,
            new_status='IN_TRANSIT'
        )
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        mock_logger.error.assert_called()

if __name__ == '__main__':
    import unittest
    unittest.main()