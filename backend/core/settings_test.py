# settings_test.py
import os
import sys
from pathlib import Path
from datetime import timedelta

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# CONFIGURACIÓN BÁSICA
# ==============================================================================

SECRET_KEY = 'test-secret-key-for-testing-only-1234567890abcdefghijklmnopqrstuvwxyz'
DEBUG = True
ALLOWED_HOSTS = ['*', 'testserver']

# ==============================================================================
# CONFIGURACIÓN DE BASE DE DATOS (SQLite en memoria para testing más rápido)
# ==============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # Usar base de datos en memoria para tests más rápidos
        'TEST': {
            'NAME': ':memory:',
        }
    }
}

# ==============================================================================
# APLICACIONES Y MIDDLEWARE
# ==============================================================================

INSTALLED_APPS = [
    # Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_yasg',
    'django_filters',
    
    # Custom apps
    'users',
    'cattle', 
    'iot',
    'blockchain',
    'core',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ==============================================================================
# REST FRAMEWORK - Configuración optimizada para testing
# ==============================================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'DEFAULT_THROTTLE_CLASSES': [],
    'DEFAULT_THROTTLE_RATES': {
        'user': None,
        'anon': None,
    }
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),  # Más corto para tests
    'REFRESH_TOKEN_LIFETIME': timedelta(hours=1),
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
}

# ==============================================================================
# CONFIGURACIÓN BLOCKCHAIN PARA TESTING (Mocks)
# ==============================================================================

BLOCKCHAIN_RPC_URL = 'https://polygon-amoy.g.alchemy.com/v2/test'
BLOCKCHAIN_CHAIN_ID = 80002
ADMIN_PRIVATE_KEY = '0x' + '1' * 64  # 64 chars hex con prefijo 0x
GANADO_TOKEN_ADDRESS = '0x' + '1' * 40
ANIMAL_NFT_ADDRESS = '0x' + '2' * 40
REGISTRY_ADDRESS = '0x' + '3' * 40
IPFS_GATEWAY_URL = 'https://ipfs.io/ipfs/'
MAX_GAS_PRICE = 100000000000
MIN_GAS_PRICE = 1000000000
DEFAULT_GAS_LIMIT = 21000
TRANSACTION_TIMEOUT = 30  # Reducido para tests
SYNC_INTERVAL = 10  # Reducido para tests
HEALTH_CHECK_INTERVAL = 60  # Reducido para tests
MAX_RETRIES = 2  # Reducido para tests
VERSION = '1.0.0-test'

CONTRACTS_DIR = os.path.join(BASE_DIR, '../artifacts/contracts')

# ==============================================================================
# CONFIGURACIONES ADICIONALES OPTIMIZADAS PARA TESTING
# ==============================================================================

LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

AUTH_USER_MODEL = 'users.User'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Password hashers más rápidos para testing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Desactivar logging durante tests
import logging
logging.disable(logging.CRITICAL)

# Configuración de CORS para testing
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Configuración de email para testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Cache para testing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Configuración para testing
TESTING = True
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Deshabilitar checks que no son necesarios en testing
SILENCED_SYSTEM_CHECKS = [
    'security.W001',  # No need for security warnings in tests
    'security.W002',  # No need for security warnings in tests
    'security.W003',  # No need for security warnings in tests
    'security.W004',  # No need for security warnings in tests
    'security.W005',  # No need for security warnings in tests
    'security.W006',  # No need for security warnings in tests
    'security.W007',  # No need for security warnings in tests
    'security.W008',  # No need for security warnings in tests
    'security.W009',  # No need for security warnings in tests
    'security.W010',  # No need for security warnings in tests
    'security.W011',  # No need for security warnings in tests
    'security.W012',  # No need for security warnings in tests
    'security.W013',  # No need for security warnings in tests
    'security.W014',  # No need for security warnings in tests
    'security.W015',  # No need for security warnings in tests
    'security.W016',  # No need for security warnings in tests
    'security.W017',  # No need for security warnings in tests
    'security.W018',  # No need for security warnings in tests
    'security.W019',  # No need for security warnings in tests
    'security.W020',  # No need for security warnings in tests
    'security.W021',  # No need for security warnings in tests
]