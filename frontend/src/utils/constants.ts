// constants.ts

// Application
export const APP_NAME = import.meta.env.VITE_APP_NAME || 'GanadoChain';
export const APP_VERSION = import.meta.env.VITE_APP_VERSION || '1.0.0';

// Blockchain - Polygon Amoy
export const BLOCKCHAIN_NETWORK = import.meta.env.VITE_BLOCKCHAIN_NETWORK || 'polygon-amoy';
export const BLOCKCHAIN_RPC_URL = import.meta.env.VITE_BLOCKCHAIN_RPC_URL || 'https://rpc-amoy.polygon.technology';
export const CHAIN_ID = parseInt(import.meta.env.VITE_CHAIN_ID || '80002');
export const EXPLORER_URL = import.meta.env.VITE_EXPLORER_URL || 'https://amoy.polygonscan.com';

// Contract Addresses
export const GANADO_TOKEN_ADDRESS = import.meta.env.VITE_GANADO_TOKEN_ADDRESS || '0x1d663FB788D01Cc7F2C98549A100Bc0b4C2a4430';
export const ANIMAL_NFT_ADDRESS = import.meta.env.VITE_ANIMAL_NFT_ADDRESS || '0xB37AF476c029Ec1C0056988d3Ce0b20aA3ea9F66';
export const REGISTRY_ADDRESS = import.meta.env.VITE_REGISTRY_ADDRESS || '0x04eF92BB7C1b3CDC22e941cEAB2206311C57ef68';

// Wallet Administration
export const ADMIN_WALLET_ADDRESS = import.meta.env.VITE_ADMIN_WALLET_ADDRESS || '0xF27c409539AC5a5deB6fe0FCac5434AD9867B310';

// Safe Addresses
export const SAFE_DEPLOYER1 = import.meta.env.VITE_SAFE_DEPLOYER1 || '0xb189f4a9e0dd3db093292a4774c77b196647d6c1';
export const SAFE_DEPLOYER2 = import.meta.env.VITE_SAFE_DEPLOYER2 || '0x02797b470c81e5fdd827602b60bbe1b831ac43d1';
export const SAFE_DEPLOYER3 = import.meta.env.VITE_SAFE_DEPLOYER3 || '0x0d123e3501868e865f68eed74f4edcf97fa1f023';

// API Keys
export const ETHERSCAN_API_KEY = import.meta.env.VITE_ETHERSCAN_API_KEY || 'B575EDK97J1KQMVJ7PP7G2EK2QTCRYREN2';
export const IPFS_GATEWAY_URL = import.meta.env.VITE_IPFS_GATEWAY_URL || 'https://ipfs.io/ipfs';

// Backend API
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
export const API_TIMEOUT = parseInt(import.meta.env.VITE_API_TIMEOUT || '10000');

// IoT Configuration
export const IOT_API_KEY = import.meta.env.VITE_IOT_API_KEY || 'tu-iot-api-key-secreta';
export const GPS_UPDATE_INTERVAL = parseInt(import.meta.env.VITE_GPS_UPDATE_INTERVAL || '300');
export const SENSOR_DATA_TIMEOUT = parseInt(import.meta.env.VITE_SENSOR_DATA_TIMEOUT || '60');

// Web3 Provider
export const WEB3_PROVIDER_URL = import.meta.env.VITE_WEB3_PROVIDER_URL || 'https://rpc-amoy.polygon.technology';

// JWT Configuration
export const JWT_ACCESS_TOKEN_KEY = import.meta.env.VITE_JWT_ACCESS_TOKEN_KEY || 'access_token';
export const JWT_REFRESH_TOKEN_KEY = import.meta.env.VITE_JWT_REFRESH_TOKEN_KEY || 'refresh_token';

// Auth Routes
export const LOGIN_URL = import.meta.env.VITE_LOGIN_URL || '/api/users/auth/login/';
export const REFRESH_TOKEN_URL = import.meta.env.VITE_REFRESH_TOKEN_URL || '/api/users/auth/token/refresh/';
export const REGISTER_URL = import.meta.env.VITE_REGISTER_URL || '/api/users/auth/register/';
export const WALLET_CONNECT_URL = import.meta.env.VITE_WALLET_CONNECT_URL || '/api/users/wallet/connect/';
export const USER_PROFILE_URL = '/api/users/profile/';

// Additional API Routes (si es necesario)
// export const ANIMAL_API_URL = '/api/animals/';
// export const TRANSACTION_API_URL = '/api/transactions/';
// export const IOT_DEVICE_API_URL = '/api/iot/devices/';