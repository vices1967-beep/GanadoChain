from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from cattle.models import Animal, AnimalHealthRecord, HealthStatus
from iot.models import IoTDevice
from decimal import Decimal

User = get_user_model()

class HealthServiceTests(APITestCase):
    """Tests para los métodos de salud e IoT en services.py"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='vet',
            email='vet@example.com',
            password='testpass123',
            wallet_address='0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
            role='VET_ROLE'
        )
        
        self.animal = Animal.objects.create(
            ear_tag='HEALTH001',
            breed='Angus',
            birth_date='2023-01-01',
            weight=500.00,
            health_status=HealthStatus.HEALTHY,
            location='Test Farm',
            owner=self.user,
            ipfs_hash='QmHealthHash',
            token_id=123,
            nft_owner_wallet=self.user.wallet_address
        )
        
        self.iot_device = IoTDevice.objects.create(
            device_id='IOT001',
            device_type='TEMPERATURE_SENSOR',
            status='ACTIVE',
            owner=self.user
        )

    @patch('blockchain.services.logger')
    @patch('blockchain.services.BlockchainService.__init__', return_value=None)
    def test_update_animal_health_comprehensive_vet(self, mock_init, mock_logger):
        """Test para update_animal_health completo desde veterinario"""
        from ..services import BlockchainService
        
        service = BlockchainService()
        service.w3 = MagicMock()
        service.wallet_address = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        service.private_key = 'test_private_key'
        service.nft_contract = MagicMock()
        
        # Mockear las llamadas a blockchain
        service.nft_contract.functions.updateOperational.return_value.build_transaction.return_value = {}
        service.w3.eth.account.sign_transaction.return_value.rawTransaction = b'signed_tx'
        service.w3.eth.send_raw_transaction.return_value.hex.return_value = '0xhealthtx'
        service.w3.eth.get_transaction_count.return_value = 1
        service.w3.eth.wait_for_transaction_receipt = MagicMock(return_value={'status': 1})
        
        tx_hash = service.update_animal_health(
            animal_id=self.animal.id,
            health_status=HealthStatus.SICK,
            source='VETERINARIAN',
            veterinarian_wallet=self.user.wallet_address,
            notes='Animal con fiebre',
            temperature=39.8,
            heart_rate=95
        )
        
        self.assertEqual(tx_hash, '0xhealthtx')
        
        # Verificar que se creó el registro de salud
        record = AnimalHealthRecord.objects.get(animal=self.animal)
        self.assertEqual(record.health_status, HealthStatus.SICK)
        self.assertEqual(record.source, 'VETERINARIAN')
        self.assertEqual(float(record.temperature), 39.8)
        self.assertEqual(record.heart_rate, 95)
        self.assertEqual(record.notes, 'Animal con fiebre')
        self.assertEqual(record.veterinarian, self.user)

    @patch('blockchain.services.logger')
    @patch('blockchain.services.BlockchainService.__init__', return_value=None)
    def test_update_animal_health_iot_comprehensive(self, mock_init, mock_logger):
        """Test para update_animal_health completo desde IoT"""
        from ..services import BlockchainService
        
        service = BlockchainService()
        service.w3 = MagicMock()
        service.wallet_address = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        service.private_key = 'test_private_key'
        service.nft_contract = MagicMock()
        
        # Mockear las llamadas a blockchain
        service.nft_contract.functions.updateOperational.return_value.build_transaction.return_value = {}
        service.w3.eth.account.sign_transaction.return_value.rawTransaction = b'signed_tx'
        service.w3.eth.send_raw_transaction.return_value.hex.return_value = '0xhealthtx'
        service.w3.eth.get_transaction_count.return_value = 1
        service.w3.eth.wait_for_transaction_receipt = MagicMock(return_value={'status': 1})
        
        tx_hash = service.update_animal_health(
            animal_id=self.animal.id,
            health_status=HealthStatus.SICK,
            source='IOT_SENSOR',
            iot_device_id='IOT001',
            temperature=39.5,
            heart_rate=85,
            notes='Lectura anómala del sensor'
        )
        
        self.assertEqual(tx_hash, '0xhealthtx')
        
        # Verificar que se creó el registro de salud con datos IoT
        record = AnimalHealthRecord.objects.get(animal=self.animal)
        self.assertEqual(record.health_status, HealthStatus.SICK)
        self.assertEqual(record.source, 'IOT_SENSOR')
        self.assertEqual(record.iot_device_id, 'IOT001')
        self.assertEqual(float(record.temperature), 39.5)
        self.assertEqual(record.heart_rate, 85)
        self.assertEqual(record.notes, 'Lectura anómala del sensor')

    @patch('blockchain.services.logger')
    @patch('blockchain.services.BlockchainService.__init__', return_value=None)
    def test_update_animal_health_minimal_params(self, mock_init, mock_logger):
        """Test para update_animal_health con parámetros mínimos"""
        from ..services import BlockchainService
        
        service = BlockchainService()
        service.w3 = MagicMock()
        service.wallet_address = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        service.private_key = 'test_private_key'
        service.nft_contract = MagicMock()
        
        # Mockear las llamadas a blockchain
        service.nft_contract.functions.updateOperational.return_value.build_transaction.return_value = {}
        service.w3.eth.account.sign_transaction.return_value.rawTransaction = b'signed_tx'
        service.w3.eth.send_raw_transaction.return_value.hex.return_value = '0xhealthtx'
        service.w3.eth.get_transaction_count.return_value = 1
        service.w3.eth.wait_for_transaction_receipt = MagicMock(return_value={'status': 1})
        
        tx_hash = service.update_animal_health(
            animal_id=self.animal.id,
            health_status=HealthStatus.UNDER_OBSERVATION,
            source='SYSTEM'
        )
        
        self.assertEqual(tx_hash, '0xhealthtx')
        
        # Verificar que se creó el registro básico
        record = AnimalHealthRecord.objects.get(animal=self.animal)
        self.assertEqual(record.health_status, HealthStatus.UNDER_OBSERVATION)
        self.assertEqual(record.source, 'SYSTEM')

    @patch('blockchain.services.logger')
    @patch('blockchain.services.BlockchainService.__init__', return_value=None)
    def test_update_health_from_iot_success(self, mock_init, mock_logger):
        """Test para update_health_from_iot exitoso"""
        from ..services import BlockchainService
        
        service = BlockchainService()
        service.update_animal_health = MagicMock(return_value='0xiothealthtx')
        
        result = service.update_health_from_iot(
            animal_id=self.animal.id,
            health_status=HealthStatus.SICK,
            device_id='IOT001',
            temperature=39.5,
            heart_rate=85
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['tx_hash'], '0xiothealthtx')
        service.update_animal_health.assert_called_once()

    @patch('blockchain.services.logger')
    @patch('blockchain.services.BlockchainService.__init__', return_value=None)
    def test_update_health_from_iot_with_anomalies(self, mock_init, mock_logger):
        """Test para update_health_from_iot con anomalías"""
        from ..services import BlockchainService
        
        service = BlockchainService()
        service.update_animal_health = MagicMock(return_value='0xiottx')
        
        # CORRECCIÓN: Eliminar el parámetro 'notes' que no existe
        result = service.update_health_from_iot(
            animal_id=self.animal.id,
            health_status=HealthStatus.SICK,
            device_id='IOT001',
            temperature=40.2,
            heart_rate=110
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['tx_hash'], '0xiottx')
        
        # Verificar que se llamó con los parámetros correctos
        call_args = service.update_animal_health.call_args[1]
        self.assertEqual(call_args['health_status'], HealthStatus.SICK)
        self.assertEqual(call_args['iot_device_id'], 'IOT001')
        self.assertEqual(call_args['temperature'], 40.2)
        self.assertEqual(call_args['heart_rate'], 110)
        
        # CORRECCIÓN: Verificar el formato automático de notes
        self.assertIn('Datos automáticos desde IoT', call_args['notes'])
        self.assertIn('40.2°C', call_args['notes'])
        self.assertIn('110bpm', call_args['notes'])

    @patch('blockchain.services.logger')
    @patch('blockchain.services.BlockchainService.__init__', return_value=None)
    def test_update_animal_health_no_token_id(self, mock_init, mock_logger):
        """Test para update_animal_health sin token_id"""
        from ..services import BlockchainService
        
        service = BlockchainService()
        self.animal.token_id = None
        self.animal.save()
        
        with self.assertRaises(Exception) as context:
            service.update_animal_health(
                animal_id=self.animal.id,
                health_status=HealthStatus.SICK
            )
        
        self.assertIn('no tiene NFT', str(context.exception))

    @patch('blockchain.services.logger')
    @patch('blockchain.services.BlockchainService.__init__', return_value=None)
    def test_update_animal_health_nonexistent_animal(self, mock_init, mock_logger):
        """Test para update_animal_health con animal inexistente"""
        from ..services import BlockchainService
        
        service = BlockchainService()
        
        with self.assertRaises(Exception) as context:
            service.update_animal_health(
                animal_id=9999,
                health_status=HealthStatus.SICK
            )
        
        self.assertIn('Animal', str(context.exception))

    @patch('blockchain.services.logger')
    @patch('blockchain.services.BlockchainService.__init__', return_value=None)
    def test_update_animal_health_nonexistent_vet(self, mock_init, mock_logger):
        """Test para update_animal_health con veterinario inexistente"""
        from ..services import BlockchainService
        
        service = BlockchainService()
        service.w3 = MagicMock()
        service.wallet_address = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        service.private_key = 'test_private_key'
        service.nft_contract = MagicMock()
        
        # Mockear las llamadas a blockchain
        service.nft_contract.functions.updateOperational.return_value.build_transaction.return_value = {}
        service.w3.eth.account.sign_transaction.return_value.rawTransaction = b'signed_tx'
        service.w3.eth.send_raw_transaction.return_value.hex.return_value = '0xhealthtx'
        service.w3.eth.get_transaction_count.return_value = 1
        service.w3.eth.wait_for_transaction_receipt = MagicMock(return_value={'status': 1})
        
        tx_hash = service.update_animal_health(
            animal_id=self.animal.id,
            health_status=HealthStatus.SICK,
            source='VETERINARIAN',
            veterinarian_wallet='0x0000000000000000000000000000000000000000',
            notes='Animal tratado por veterinario externo'
        )
        
        self.assertEqual(tx_hash, '0xhealthtx')
        
        record = AnimalHealthRecord.objects.get(animal=self.animal)
        self.assertEqual(record.health_status, HealthStatus.SICK)
        self.assertIsNone(record.veterinarian)
        self.assertEqual(record.notes, 'Animal tratado por veterinario externo')

    @patch('blockchain.services.logger')
    @patch('blockchain.services.BlockchainService.__init__', return_value=None)
    def test_update_animal_health_nonexistent_iot_device(self, mock_init, mock_logger):
        """Test para update_animal_health con dispositivo IoT inexistente"""
        from ..services import BlockchainService
        
        service = BlockchainService()
        service.w3 = MagicMock()
        service.wallet_address = '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
        service.private_key = 'test_private_key'
        service.nft_contract = MagicMock()
        
        # Mockear las llamadas a blockchain
        service.nft_contract.functions.updateOperational.return_value.build_transaction.return_value = {}
        service.w3.eth.account.sign_transaction.return_value.rawTransaction = b'signed_tx'
        service.w3.eth.send_raw_transaction.return_value.hex.return_value = '0xhealthtx'
        service.w3.eth.get_transaction_count.return_value = 1
        service.w3.eth.wait_for_transaction_receipt = MagicMock(return_value={'status': 1})
        
        tx_hash = service.update_animal_health(
            animal_id=self.animal.id,
            health_status=HealthStatus.HEALTHY,
            source='IOT_SENSOR',
            iot_device_id='NONEXISTENT_DEVICE',
            temperature=38.5,
            heart_rate=75
        )
        
        self.assertEqual(tx_hash, '0xhealthtx')
        
        record = AnimalHealthRecord.objects.get(animal=self.animal)
        self.assertEqual(record.health_status, HealthStatus.HEALTHY)
        self.assertEqual(record.iot_device_id, 'NONEXISTENT_DEVICE')

if __name__ == '__main__':
    import unittest
    unittest.main()