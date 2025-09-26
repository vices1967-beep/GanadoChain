import os
import sys
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# ==============================================================================
# CONFIGURACIÓN INICIAL
# ==============================================================================

# ==============================================================================
# CONFIGURACIÓN INICIAL - CORREGIR ESTA PARTE
# ==============================================================================

# CORREGIR: Especificar la ruta correcta del .env
BASE_DIR = Path(__file__).resolve().parent.parent  # Esto apunta a /GanadoChain/backend
env_path = BASE_DIR / '.env'  # Ruta correcta: /GanadoChain/backend/.env

print(f"🔧 Cargando variables de entorno desde: {env_path}")
print(f"🔧 El archivo .env existe: {env_path.exists()}")

# Cargar variables de entorno desde la ruta correcta
load_dotenv(env_path)

# Verificar que se cargan las variables de Starknet
print(f"✅ STARKNET_RPC_URL cargado: {bool(os.getenv('STARKNET_RPC_URL'))}")
print(f"✅ BLOCKCHAIN_RPC_URL cargado: {bool(os.getenv('BLOCKCHAIN_RPC_URL'))}")

# ==============================================================================
# CONFIGURACIÓN DE URLS
# ==============================================================================

ROOT_URLCONF = 'core.urls'


# ==============================================================================
# SEGURIDAD - CONFIGURACIÓN CRÍTICA
# ==============================================================================

# SECRET_KEY con validación
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    if 'test' in sys.argv or 'test_coverage' in sys.argv:
        SECRET_KEY = 'test-secret-key-for-testing-only'
    else:
        raise ValueError("DJANGO_SECRET_KEY no está configurada en las variables de entorno")

# Debug mode con validación
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Allowed hosts con validación
ALLOWED_HOSTS = []
hosts = os.getenv('ALLOWED_HOSTS', '')
if hosts:
    ALLOWED_HOSTS = [host.strip() for host in hosts.split(',') if host.strip()]
else:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# ==============================================================================
# CONFIGURACIÓN DE BASE DE DATOS MEJORADA
# ==============================================================================

# PostgreSQL ( desarrollo y producción)
if os.getenv('DATABASE_URL'):
    # PostgreSQL desde DATABASE_URL (para producción)
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(
            default=os.getenv('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # POSTGIS PARA DESARROLLO LOCAL (¡CORRECTO!)
    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST'),
            'PORT': os.getenv('DB_PORT'),
        }
    }

# ==============================================================================
# APLICACIONES Y MIDDLEWARE
# ==============================================================================

INSTALLED_APPS = [
    # Django core
    'corsheaders',  # ← ¡DEBE IR AL PRINCIPIO!
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    
    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'django_filters',
    
    # Custom apps
    'users',
    'cattle', 
    'iot',
    'blockchain',
    'core',  # ✅ Asegurar que core está aquí
    'market',
    'governance',
    'consumer',
    'rewards',
    'analytics',
    'reports',
    'certification',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Para static files en producción
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
# ==============================================================================
# CONFIGURACIÓN DE TEMPLATES
# ==============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Directorio para templates personalizados
        'APP_DIRS': True,  # IMPORTANTE: debe ser True para que el admin funcione
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
# REST FRAMEWORK MEJORADO
# ==============================================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
        'burst': '60/minute',
        'sustained': '1000/day'
    },
    'EXCEPTION_HANDLER': 'core.exceptions.custom_exception_handler',
}

# Configuración Simple JWT mejorada
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=60),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# ==============================================================================
# CONFIGURACIÓN BLOCKCHAIN MEJORADA
# ==============================================================================

# Validación de direcciones de contratos
# ==============================================================================
# CONFIGURACIÓN BLOCKCHAIN MEJORADA - AÑADIR STARKNET
# ==============================================================================

# Validación de direcciones de contratos
def validate_ethereum_address(address):
    if address and address != '' and not address.startswith('0x'):
        raise ValueError(f"Dirección Ethereum inválida: {address}")
    return address

def validate_starknet_address(address):
    if address and address != '' and not address.startswith('0x'):
        raise ValueError(f"Dirección Starknet inválida: {address}")
    return address

BLOCKCHAIN_CONFIG = {
    'NETWORK': os.getenv('BLOCKCHAIN_NETWORK', 'polygon-amoy'),
    'RPC_URL': os.getenv('BLOCKCHAIN_RPC_URL', 'https://rpc-amoy.polygon.technology'),
    'CHAIN_ID': int(os.getenv('CHAIN_ID', 80002)),
    'EXPLORER_URL': os.getenv('EXPLORER_URL', 'https://amoy.polygonscan.com'),
    'CONTRACTS': {
        'GANADO_TOKEN': validate_ethereum_address(os.getenv('GANADO_TOKEN_ADDRESS')),
        'ANIMAL_NFT': validate_ethereum_address(os.getenv('ANIMAL_NFT_ADDRESS')),
        'REGISTRY': validate_ethereum_address(os.getenv('REGISTRY_ADDRESS')),
    },
    'ADMIN_WALLET': validate_ethereum_address(os.getenv('ADMIN_WALLET_ADDRESS')),
    'SAFE_ADDRESSES': [
        validate_ethereum_address(os.getenv('SAFE_DEPLOYER1', '')),
        validate_ethereum_address(os.getenv('SAFE_DEPLOYER2', '')),
        validate_ethereum_address(os.getenv('SAFE_DEPLOYER3', '')),
    ],
    'API_KEYS': {
        'ETHERSCAN': os.getenv('ETHERSCAN_API_KEY'),
        'IPFS_URL': os.getenv('IPFS_API_URL', '/ip4/127.0.0.1/tcp/5001'),
    }
}

# AÑADIR CONFIGURACIÓN STARKNET
STARKNET_CONFIG = {
    'NETWORK': os.getenv('STARKNET_NETWORK', 'sepolia'),
    'RPC_URL1': os.getenv('STARKNET_RPC_URL1', 'https://sepolia.starknet.io'),
    'RPC_URL': os.getenv('STARKNET_RPC_URL', 'https://starknet-sepolia.infura.io/v3/5e66662444bb43dbbce887f21f69c894'),
    'EXPLORER_URL': os.getenv('STARKNET_EXPLORER_URL', 'https://sepolia.starkscan.co'),
    'ACCOUNT_ADDRESS': validate_starknet_address(os.getenv('STARKNET_ACCOUNT_ADDRESS')),
    'PRIVATE_KEY': os.getenv('STARKNET_PRIVATE_KEY'),
    'PUBLIC_KEY': os.getenv('STARKNET_PUBLIC_KEY'),
    'CONTRACTS': {
        'NFT_PROXY': validate_starknet_address(os.getenv('STARKNET_NFT_PROXY_ADDRESS')),
        'NFT_IMPLEMENTATION': validate_starknet_address(os.getenv('STARKNET_NFT_IMPLEMENTATION_ADDRESS')),
        'REGISTRY_PROXY': validate_starknet_address(os.getenv('STARKNET_REGISTRY_PROXY_ADDRESS')),
        'REGISTRY_IMPLEMENTATION': validate_starknet_address(os.getenv('STARKNET_REGISTRY_IMPLEMENTATION_ADDRESS')),
    }
}

# CONFIGURACIÓN MULTICHAIN
MULTICHAIN_CONFIG = {
    'DEFAULT_BLOCKCHAIN': os.getenv('DEFAULT_BLOCKCHAIN', 'POLYGON'),
    'ENABLED_BLOCKCHAINS': [chain.strip() for chain in os.getenv('ENABLED_BLOCKCHAINS', 'POLYGON,STARKNET').split(',')],
    'BLOCKCHAINS': {
        'POLYGON': BLOCKCHAIN_CONFIG,
        'STARKNET': STARKNET_CONFIG
    }
}

# ==============================================================================
# CORS Y SEGURIDAD
# ==============================================================================

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

CORS_ALLOW_CREDENTIALS = True

# Opcional: si quieres permitir ciertos headers
CORS_ALLOW_HEADERS = [
    'accept',
    'authorization',
    'content-type',
    'x-csrftoken',
    'x-requested-with',
]

# Opcional: permitir solo métodos necesarios
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS.copy()

# Configuración de seguridad adicional
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin-allow-popups'
SECURE_REFERRER_POLICY = 'same-origin'

# ==============================================================================
# INTERNATIONALIZATION
# ==============================================================================

LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Argentina/Buenos_Aires'  # Más específico para tu ubicación
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ==============================================================================
# ARCHIVOS ESTÁTICOS Y MEDIA
# ==============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Configuración Whitenoise para producción
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ==============================================================================
# LOGGING MEJORADO
# ==============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'json': {
            'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(module)s", "message": "%(message)s"}',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple' if DEBUG else 'json',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'blockchain_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'blockchain.log',
            'maxBytes': 1024 * 1024 * 20,  # 20 MB
            'backupCount': 3,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'blockchain': {
            'handlers': ['console', 'blockchain_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'iot': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'users': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ==============================================================================
# CONFIGURACIÓN DE SEGURIDAD PARA PRODUCCIÓN
# ==============================================================================

if not DEBUG:
    # HTTPS settings
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Security headers
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Additional security
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True

# ==============================================================================
# CONFIGURACIONES ADICIONALES
# ==============================================================================

# Custom user model
AUTH_USER_MODEL = 'users.User'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================================================================
# CONFIGURACIÓN PARA DRF-YASG (SWAGGER)
# ==============================================================================
SPECTACULAR_SETTINGS = {
    'TITLE': 'GanadoChain API',
    'DESCRIPTION': 'Blockchain Cattle Tracking System',
    'VERSION': '1.0.0',
}
# # ==============================================================================
# VALIDACIONES FINALES
# ==============================================================================

# Validar que las variables críticas estén configuradas
if not DEBUG:
    required_env_vars = [
        'DJANGO_SECRET_KEY',
        'DATABASE_URL',
        'ADMIN_WALLET_ADDRESS',
    ]
    
    for var in required_env_vars:
        if not os.getenv(var):
            raise ValueError(f"Variable de entorno requerida no configurada: {var}")

# Crear directorio de logs si no existe
(BASE_DIR / 'logs').mkdir(exist_ok=True)

# Crear directorio de templates si no existe
(BASE_DIR / 'templates').mkdir(exist_ok=True)

# Crear directorio static si no existe
(BASE_DIR / 'static').mkdir(exist_ok=True)


# Añadir al final del archivo
INSTALLED_APPS += [
    'django.contrib.gis',
]

# settings.py (al final)
# Blockchain Configuration
WEB3_PROVIDER = os.environ.get('WEB3_PROVIDER_URL', 'https://rpc-amoy.polygon.technology')
CONTRACT_ADDRESS = os.environ.get('CONTRACT_ADDRESS', '0x04eF92BB7C1b3CDC22e941cEAB2206311C57ef68')


# ==============================================================================
# VARIABLES DIRECTAS PARA COMPATIBILIDAD - CORRECCIONES FINALES
# ==============================================================================

# Variables directas para compatibilidad con código existente
BLOCKCHAIN_RPC_URL = BLOCKCHAIN_CONFIG['RPC_URL']
STARKNET_RPC_URL = STARKNET_CONFIG['RPC_URL']
WEB3_PROVIDER_URL = BLOCKCHAIN_CONFIG['RPC_URL']
CONTRACT_ADDRESS = BLOCKCHAIN_CONFIG['CONTRACTS']['ANIMAL_NFT']

# Configuración adicional para evitar errores
BLOCKCHAIN_NETWORK = BLOCKCHAIN_CONFIG['NETWORK']
CHAIN_ID = BLOCKCHAIN_CONFIG['CHAIN_ID']
EXPLORER_URL = BLOCKCHAIN_CONFIG['EXPLORER_URL']
GANADO_TOKEN_ADDRESS = BLOCKCHAIN_CONFIG['CONTRACTS']['GANADO_TOKEN']
ANIMAL_NFT_ADDRESS = BLOCKCHAIN_CONFIG['CONTRACTS']['ANIMAL_NFT']
REGISTRY_ADDRESS = BLOCKCHAIN_CONFIG['CONTRACTS']['REGISTRY']
ADMIN_WALLET_ADDRESS = BLOCKCHAIN_CONFIG['ADMIN_WALLET']

# Variables críticas del .env
ADMIN_PRIVATE_KEY = os.getenv('ADMIN_PRIVATE_KEY')
INFURA_PROJECT_ID = os.getenv('INFURA_PROJECT_ID')
IPFS_API_URL = os.getenv('IPFS_API_URL', '/ip4/127.0.0.1/tcp/5001')
IOT_API_KEY = os.getenv('IOT_API_KEY', 'default-iot-key')

# Safe addresses
SAFE_ADDRESSES = [
    os.getenv('SAFE_DEPLOYER1'),
    os.getenv('SAFE_DEPLOYER2'), 
    os.getenv('SAFE_DEPLOYER3')
]

# Starknet configuration
STARKNET_ACCOUNT_ADDRESS = os.getenv('STARKNET_ACCOUNT_ADDRESS')
STARKNET_PRIVATE_KEY = os.getenv('STARKNET_PRIVATE_KEY')
STARKNET_PUBLIC_KEY = os.getenv('STARKNET_PUBLIC_KEY')

print("✅ Todas las variables de compatibilidad cargadas correctamente")