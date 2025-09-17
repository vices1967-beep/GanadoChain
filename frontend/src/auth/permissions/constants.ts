// constants.ts - Endpoints de API

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
export const LOGIN_URL = import.meta.env.VITE_LOGIN_URL || '/api/auth/login/';
export const REFRESH_TOKEN_URL = import.meta.env.VITE_REFRESH_TOKEN_URL || '/api/auth/token/refresh/';
export const REGISTER_URL = import.meta.env.VITE_REGISTER_URL || '/api/auth/register/';
export const WALLET_CONNECT_URL = import.meta.env.VITE_WALLET_CONNECT_URL || '/api/users/wallet/connect/';
export const USER_PROFILE_URL = '/api/users/profile/';

// ==========================================================================
// ENDPOINTS DE API POR MÓDULO
// ==========================================================================

// --------------------------------------------------------------------------
// CORE - Endpoints del sistema central
// --------------------------------------------------------------------------
export const SYSTEM_METRICS_URL = '/api/core/metrics/';
export const HEALTH_CHECK_URL = '/api/core/health/';
export const SYSTEM_CONFIG_URL = '/api/core/config/';
export const DASHBOARD_STATS_URL = '/api/core/dashboard/stats/';
export const VALIDATION_TEST_URL = '/api/core/validate/';
export const SYSTEM_MAINTENANCE_URL = '/api/core/maintenance/';
export const API_INFO_URL = '/api/core/info/';
export const ERROR_TEST_URL = '/api/core/error-test/';

// --------------------------------------------------------------------------
// USERS - Gestión de usuarios y autenticación
// --------------------------------------------------------------------------
export const USERS_MANAGEMENT_URL = '/api/users/users/';
export const USER_PREFERENCES_URL = '/api/users/preferences/';
export const API_TOKENS_URL = '/api/users/api-tokens/';
export const USER_ACTIVITY_LOGS_URL = '/api/users/activity-logs/';
export const NOTIFICATIONS_URL = '/api/users/notifications/';

// --------------------------------------------------------------------------
// ANALYTICS - Análisis y reportes
// --------------------------------------------------------------------------
export const GENETIC_ANALYTICS_URL = '/api/analytics/genetic/';
export const HEALTH_TRENDS_URL = '/api/analytics/health-trends/';
export const SUPPLY_CHAIN_ANALYTICS_URL = '/api/analytics/supply-chain/';
export const SUSTAINABILITY_METRICS_URL = '/api/analytics/sustainability/';
export const BLOCKCHAIN_ANALYTICS_URL = '/api/analytics/blockchain/';
export const SYSTEM_PERFORMANCE_URL = '/api/analytics/system-performance/';
export const PREDICTIVE_ANALYTICS_URL = '/api/analytics/predictive/';
export const CUSTOM_REPORTS_URL = '/api/analytics/reports/custom/';

// --------------------------------------------------------------------------
// BLOCKCHAIN - Operaciones con blockchain
// --------------------------------------------------------------------------
export const BLOCKCHAIN_EVENTS_URL = '/api/blockchain/events/';
export const CONTRACT_INTERACTIONS_URL = '/api/blockchain/interactions/';
export const SMART_CONTRACTS_URL = '/api/blockchain/contracts/';
export const ASSIGN_ROLE_URL = '/api/blockchain/assign-role/';
export const MINT_NFT_URL = '/api/blockchain/mint/nft/';
export const CHECK_ROLE_URL = '/api/blockchain/check-role/';
export const MINT_TOKENS_URL = '/api/blockchain/mint/tokens/';
export const ANIMAL_HISTORY_URL = (id: string | number) => `/api/blockchain/animal/${id}/history/`;
export const UPDATE_HEALTH_URL = '/api/blockchain/update-health/';
export const IOT_HEALTH_DATA_URL = '/api/blockchain/iot/health-data/';
export const SMART_CONTRACT_ADMIN_URL = '/api/blockchain/advanced/contracts/admin/';
export const GAS_OPTIMIZATION_URL = '/api/blockchain/advanced/gas/optimize/';

// --------------------------------------------------------------------------
// CATTLE - Gestión de ganado
// --------------------------------------------------------------------------
export const ANIMALS_MANAGEMENT_URL = '/api/cattle/animals/';
export const ANIMAL_HEALTH_RECORDS_URL = '/api/cattle/health-records/';
export const BATCHES_MANAGEMENT_URL = '/api/cattle/batches/';
export const SEARCH_ANIMALS_URL = '/api/cattle/animals/search/';
export const SEARCH_BATCHES_URL = '/api/cattle/batches/search/';
export const CATTLE_STATS_URL = '/api/cattle/stats/';
export const CERTIFICATION_STANDARDS_URL = '/api/cattle/certification-standards/';
export const ANIMAL_CERTIFICATIONS_URL = '/api/cattle/animal-certifications/';

// --------------------------------------------------------------------------
// CONSUMER - Endpoints para consumidores
// --------------------------------------------------------------------------
export const QR_VERIFICATION_URL = '/api/consumer/verify/';
export const PUBLIC_ANIMAL_HISTORY_URL = (id: string | number) => `/api/consumer/animal/${id}/history/`;
export const GENERATE_QR_URL = (id: string | number) => `/api/consumer/animal/${id}/qr/`;
export const CONSUMER_SEARCH_URL = '/api/consumer/search/';
export const CERTIFICATION_VERIFICATION_URL = (id: string | number) => `/api/consumer/certification/${id}/verify/`;
export const BLOCKCHAIN_PROOF_URL = (id: string | number) => `/api/consumer/animal/${id}/proof/`;
export const PUBLIC_API_DOCS_URL = '/api/consumer/docs/';

// --------------------------------------------------------------------------
// GOVERNANCE - Gobierno y votaciones
// --------------------------------------------------------------------------
export const GOVERNANCE_PROPOSALS_URL = '/api/governance/proposals/';
export const VOTES_URL = '/api/governance/votes/';
export const PROPOSAL_STATS_URL = '/api/governance/stats/';
export const USER_VOTING_STATS_URL = '/api/governance/user-stats/';
export const ACTIVE_PROPOSALS_URL = '/api/governance/active/';
export const PROPOSAL_TIMELINE_URL = '/api/governance/timeline/';

// --------------------------------------------------------------------------
// IOT - Dispositivos IoT y datos de sensores
// --------------------------------------------------------------------------
export const IOT_DEVICES_URL = '/api/iot/devices/';
export const GPS_DATA_URL = '/api/iot/gps-data/';
export const HEALTH_SENSOR_DATA_URL = '/api/iot/health-data/';
export const DEVICE_EVENTS_URL = '/api/iot/device-events/';
export const IOT_DATA_INGEST_URL = '/api/iot/ingest/';
export const BULK_DATA_INGEST_URL = '/api/iot/ingest/bulk/';
export const DEVICE_REGISTRATION_URL = '/api/iot/register/';
export const IOT_STATS_URL = '/api/iot/stats/';
export const DEVICE_FIRMWARE_UPDATE_URL = (id: string | number) => `/api/iot/advanced/firmware/${id}/`;
export const BULK_DEVICE_MANAGEMENT_URL = '/api/iot/advanced/bulk-management/';
export const IOT_NETWORK_HEALTH_URL = '/api/iot/advanced/network-health/';

// --------------------------------------------------------------------------
// MARKET - Mercado y transacciones
// --------------------------------------------------------------------------
export const MARKET_LISTINGS_URL = '/api/market/listings/';
export const TRADES_URL = '/api/market/trades/';
export const MARKET_STATS_URL = '/api/market/stats/';
export const PRICE_HISTORY_URL = '/api/market/price-history/';
export const EXECUTE_TRADE_URL = (id: string | number) => `/api/market/execute-trade/${id}/`;
export const ANIMAL_MARKET_INFO_URL = (id: string | number) => `/api/market/animal/${id}/`;

// --------------------------------------------------------------------------
// REPORTS - Reportes y exportaciones
// --------------------------------------------------------------------------
export const COMPLIANCE_REPORTS_URL = '/api/reports/compliance/';
export const EXPORT_ANIMAL_DATA_URL = '/api/reports/export/animals/';
export const AUDIT_REPORTS_URL = '/api/reports/audit/';
export const FINANCIAL_REPORTS_URL = '/api/reports/financial/';
export const SYSTEM_HEALTH_REPORT_URL = '/api/reports/system-health/';
export const EXPORT_REPORTS_URL = '/api/reports/export/report/';

// --------------------------------------------------------------------------
// REWARDS - Recompensas y staking
// --------------------------------------------------------------------------
export const REWARD_DISTRIBUTION_URL = '/api/rewards/rewards/';
export const STAKING_POOLS_URL = '/api/rewards/staking/';
export const REWARD_CLAIM_URL = (id: string | number) => `/api/rewards/claim/${id}/`;
export const BULK_REWARD_CLAIM_URL = '/api/rewards/claim/bulk/';
export const STAKE_TOKENS_URL = '/api/rewards/staking/action/stake/';
export const UNSTAKE_TOKENS_URL = (id: string | number) => `/api/rewards/staking/action/unstake/${id}/`;
export const REPUTATION_LEADERBOARD_URL = '/api/rewards/leaderboard/';
export const USER_REWARDS_STATS_URL = '/api/rewards/stats/';

// src/auth/permissions/constants.ts
export enum Permission {
  // Animal permissions
  ANIMAL_VIEW = 'animal:view',
  ANIMAL_CREATE = 'animal:create',
  ANIMAL_EDIT = 'animal:edit',
  ANIMAL_DELETE = 'animal:delete',
  
  // Batch permissions
  BATCH_VIEW = 'batch:view',
  BATCH_CREATE = 'batch:create',
  BATCH_EDIT = 'batch:edit',
  BATCH_DELETE = 'batch:delete',
  
  // Certification permissions
  CERTIFICATION_VIEW = 'certification:view',
  CERTIFICATION_CREATE = 'certification:create',
  CERTIFICATION_EDIT = 'certification:edit',
  CERTIFICATION_DELETE = 'certification:delete',
  
  // User permissions
  USER_VIEW = 'user:view',
  USER_CREATE = 'user:create',
  USER_EDIT = 'user:edit',
  USER_DELETE = 'user:delete',
  
  // Admin permissions
  ADMIN_ACCESS = 'admin:access',
  SYSTEM_CONFIG = 'system:config',
  
  // IoT permissions
  IOT_VIEW = 'iot:view',
  IOT_MANAGE = 'iot:manage',
  
  // Market permissions
  MARKET_VIEW = 'market:view',
  MARKET_TRADE = 'market:trade',
  
  // Blockchain permissions
  BLOCKCHAIN_INTERACT = 'blockchain:interact',
  NFT_MINT = 'nft:mint',
}

export enum Role {
  ADMIN = 'ADMIN',
  PRODUCER = 'PRODUCER',
  VETERINARIAN = 'VETERINARIAN',
  CONSUMER = 'CONSUMER',
  AUDITOR = 'AUDITOR',
}


// Añadir si se necesita
export const ROLES = {
  ADMIN: 'ADMIN',
  PRODUCER: 'PRODUCER', 
  VETERINARIAN: 'VETERINARIAN',
  CONSUMER: 'CONSUMER',
  AUDITOR: 'AUDITOR',
} as const;