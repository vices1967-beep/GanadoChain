from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from users.serializers import (
    UserRegistrationSerializer,
    ChangePasswordSerializer,
    WalletConnectSerializer,
    PasswordResetConfirmSerializer,
    UserSearchSerializer,
)
from decimal import Decimal

User = get_user_model()

class UserRegistrationSerializerTests(TestCase):
    def setUp(self):
        self.valid_data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "ComplexPass123!",
            "password2": "ComplexPass123!",
            "first_name": "New",
            "last_name": "User",
            "wallet_address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
            "role": "PRODUCER"
        }

    def test_successful_registration(self):
        serializer = UserRegistrationSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_password_mismatch(self):
        data = self.valid_data.copy()
        data["password2"] = "DifferentPass123!"
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)
        self.assertEqual(serializer.errors['password'][0], 'Las contraseñas no coinciden.')

    def test_duplicate_email(self):
        User.objects.create_user(
            username="existing",
            email="new@example.com",
            password="testpass123",
            wallet_address="0x1234567890abcdef1234567890abcdef12345678"
        )
        serializer = UserRegistrationSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)
        self.assertEqual(serializer.errors['email'][0], 'Este correo electrónico ya está registrado.')

    def test_duplicate_wallet(self):
        User.objects.create_user(
            username="existing",
            email="existing@example.com",
            password="testpass123",
            wallet_address="0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
        )
        serializer = UserRegistrationSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("wallet_address", serializer.errors)
        self.assertEqual(serializer.errors['wallet_address'][0], 'Esta dirección wallet ya está registrada.')

    def test_invalid_wallet_address(self):
        data = self.valid_data.copy()
        data["wallet_address"] = "invalid-address"
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("wallet_address", serializer.errors)

class ChangePasswordSerializerTests(TestCase):
    def test_passwords_match(self):
        serializer = ChangePasswordSerializer(data={
            "old_password": "oldpass123",
            "new_password": "NewPass123!",
            "new_password2": "NewPass123!",
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_passwords_do_not_match(self):
        serializer = ChangePasswordSerializer(data={
            "old_password": "oldpass123",
            "new_password": "NewPass123!",
            "new_password2": "DifferentPass123!",
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn("new_password", serializer.errors)
        self.assertEqual(serializer.errors['new_password'][0], 'Las contraseñas no coinciden.')

    def test_weak_password(self):
        serializer = ChangePasswordSerializer(data={
            "old_password": "oldpass123",
            "new_password": "weak",
            "new_password2": "weak",
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn("new_password", serializer.errors)

class WalletConnectSerializerTests(TestCase):
    def test_valid_data(self):
        data = {
            "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
            "signature": "0x" + "a" * 130,  # 65 bytes en hex (130 caracteres)
            "message": "Test message for signing"
        }
        serializer = WalletConnectSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_invalid_signature_format(self):
        data = {
            "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
            "signature": "invalid-signature",  # No empieza con 0x
            "message": "Test message"
        }
        serializer = WalletConnectSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("signature", serializer.errors)
        self.assertEqual(serializer.errors['signature'][0], 'Formato de firma inválido.')

    def test_invalid_wallet_address(self):
        data = {
            "wallet_address": "invalid-address",
            "signature": "0x" + "a" * 130,
            "message": "Test message"
        }
        serializer = WalletConnectSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("wallet_address", serializer.errors)

    def test_missing_required_fields(self):
        data = {
            "wallet_address": "0x1234567890abcdef1234567890abcdef12345678"
            # Falta signature y message
        }
        serializer = WalletConnectSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("signature", serializer.errors)
        self.assertIn("message", serializer.errors)

class PasswordResetConfirmSerializerTests(TestCase):
    def test_passwords_match(self):
        data = {
            "token": "test-token-123",
            "new_password": "NewPass123!",
            "new_password2": "NewPass123!",
        }
        serializer = PasswordResetConfirmSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_passwords_do_not_match(self):
        data = {
            "token": "test-token-123",
            "new_password": "NewPass123!",
            "new_password2": "DifferentPass123!",
        }
        serializer = PasswordResetConfirmSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("new_password", serializer.errors)
        self.assertEqual(serializer.errors['new_password'][0], 'Las contraseñas no coinciden.')

    def test_missing_token(self):
        data = {
            "new_password": "NewPass123!",
            "new_password2": "NewPass123!",
        }
        serializer = PasswordResetConfirmSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("token", serializer.errors)

class UserSearchSerializerTests(TestCase):
    def test_valid_query(self):
        data = {"query": "test", "search_in": ["username", "email"]}
        serializer = UserSearchSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_query_too_long(self):
        data = {"query": "x" * 101, "search_in": ["username"]}  # Más de 100 caracteres
        serializer = UserSearchSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("query", serializer.errors)

    def test_default_search_in(self):
        data = {"query": "test"}  # search_in por defecto debería usarse
        serializer = UserSearchSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data['search_in'], ['username', 'email', 'wallet', 'name'])

    def test_invalid_search_in_choice(self):
        data = {"query": "test", "search_in": ["invalid_field"]}
        serializer = UserSearchSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("search_in", serializer.errors)