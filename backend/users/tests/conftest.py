import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def user_data():
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123',
        'wallet_address': '0x742d35Cc6634C0532925a3b844Bc454e4438f44e'
    }

@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        username='adminuser',
        email='admin@example.com',
        password='adminpass123',
        wallet_address='0x1234567890abcdef1234567890abcdef12345678'
    )