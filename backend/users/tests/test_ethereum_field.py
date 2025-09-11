# users/tests/test_ethereum_field.py
from django.test import TestCase
from rest_framework.exceptions import ValidationError
from users.serializers import EthereumAddressField

class EthereumFieldTests(TestCase):
    def test_valid_ethereum_address(self):
        field = EthereumAddressField()
        result = field.to_internal_value('0x742d35Cc6634C0532925a3b844Bc454e4438f44e')
        self.assertEqual(result, '0x742d35cc6634c0532925a3b844bc454e4438f44e')
    
    def test_invalid_ethereum_address(self):
        field = EthereumAddressField()
        with self.assertRaises(ValidationError):
            field.to_internal_value('invalid-address')
    
    def test_address_normalization(self):
        field = EthereumAddressField()
        result = field.to_internal_value('742d35cc6634c0532925a3b844bc454e4438f44e')
        self.assertEqual(result, '0x742d35cc6634c0532925a3b844bc454e4438f44e')

    # users/tests/test_ethereum_field.py - Eliminar o corregir este test
    def test_validate_method(self):
    # Este test ya no es necesario porque movimos la validación a to_internal_value
        pass
    
    # def test_validate_method(self):
    #     field = EthereumAddressField()
    #     # El método validate debería ser llamado durante serializer.is_valid()
    #     valid_value = field.validate('0x742d35cc6634c0532925a3b844bc454e4438f44e')
    #     self.assertEqual(valid_value, '0x742d35cc6634c0532925a3b844bc454e4438f44e')
        
    #     with self.assertRaises(ValidationError):
    #         field.validate('invalid-address')