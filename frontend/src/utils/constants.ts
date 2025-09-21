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
export const LOGIN_URL = '/api/users/auth/login/';
export const REFRESH_TOKEN_URL = '/api/users/auth/token/refresh/';
export const REGISTER_URL = '/api/users/auth/register/';
export const WALLET_CONNECT_URL = '/api/users/wallet/connect/';
export const USER_PROFILE_URL = '/api/users/profile/';

// Core API Routes
export const HEALTH_CHECK_URL = '/api/core/health/';
export const API_INFO_URL = '/api/core/info/';
export const SYSTEM_CONFIG_URL = '/api/core/config/';
export const DASHBOARD_STATS_URL = '/api/core/dashboard/stats/';
export const SYSTEM_METRICS_URL = '/api/core/metrics/';

// Cattle API Routes
export const ANIMALS_URL = '/api/cattle/animals/';
export const ANIMAL_SEARCH_URL = '/api/cattle/animals/search/';
export const HEALTH_RECORDS_URL = '/api/cattle/health-records/';
export const BATCHES_URL = '/api/cattle/batches/';
export const BATCH_SEARCH_URL = '/api/cattle/batches/search/';
export const CATTLE_STATS_URL = '/api/cattle/stats/';
export const CERTIFICATION_STANDARDS_URL = '/api/cattle/certification-standards/';
export const ANIMAL_CERTIFICATIONS_URL = '/api/cattle/animal-certifications/';

// Animal Operations
export const ANIMAL_MINT_NFT_URL = (id: number) => `/api/cattle/animals/${id}/mint-nft/`;
export const ANIMAL_TRANSFER_URL = (id: number) => `/api/cattle/animals/${id}/transfer/`;
export const ANIMAL_UPDATE_HEALTH_URL = (id: number) => `/api/cattle/animals/${id}/update-health/`;
export const ANIMAL_VERIFY_NFT_URL = (id: number) => `/api/cattle/animals/${id}/verify-nft/`;
export const ANIMAL_NFT_INFO_URL = (id: number) => `/api/cattle/animals/${id}/nft-info/`;
export const ANIMAL_HEALTH_RECORDS_URL = (id: number) => `/api/cattle/animals/${id}/health-records/`;
export const ANIMAL_BLOCKCHAIN_EVENTS_URL = (id: number) => `/api/cattle/animals/${id}/blockchain-events/`;
export const ANIMAL_AUDIT_TRAIL_URL = (id: number) => `/api/cattle/animals/${id}/audit-trail/`;

// Batch Operations
export const BATCH_UPDATE_STATUS_URL = (id: number) => `/api/cattle/batches/${id}/update-status/`;
export const BATCH_ADD_ANIMALS_URL = (id: number) => `/api/cattle/batches/${id}/add-animals/`;
export const BATCH_REMOVE_ANIMALS_URL = (id: number) => `/api/cattle/batches/${id}/remove-animals/`;
export const BATCH_BLOCKCHAIN_EVENTS_URL = (id: number) => `/api/cattle/batches/${id}/blockchain-events/`;
export const BATCH_AUDIT_TRAIL_URL = (id: number) => `/api/cattle/batches/${id}/audit-trail/`;

// Certification Operations
export const CERTIFICATION_REVOKE_URL = (id: number) => `/api/cattle/animal-certifications/${id}/revoke/`;

// Blockchain API Routes
export const BLOCKCHAIN_EVENTS_URL = '/api/blockchain/events/';
export const CONTRACT_INTERACTIONS_URL = '/api/blockchain/interactions/';
export const SMART_CONTRACTS_URL = '/api/blockchain/contracts/';
export const ASSIGN_ROLE_URL = '/api/blockchain/assign-role/';
export const MINT_NFT_URL = '/api/blockchain/mint/nft/';
export const CHECK_ROLE_URL = '/api/blockchain/check-role/';
export const MINT_TOKENS_URL = '/api/blockchain/mint/tokens/';
export const ANIMAL_HISTORY_URL = (id: number) => `/api/blockchain/animal/${id}/history/`;
export const UPDATE_HEALTH_URL = '/api/blockchain/update-health/';
export const IOT_HEALTH_DATA_URL = '/api/blockchain/iot/health-data/';

// IoT API Routes
export const IOT_DEVICES_URL = '/api/iot/devices/';
export const GPS_DATA_URL = '/api/iot/gps-data/';
export const HEALTH_SENSOR_DATA_URL = '/api/iot/health-data/';
export const DEVICE_EVENTS_URL = '/api/iot/device-events/';
export const IOT_DATA_INGEST_URL = '/api/iot/ingest/';
export const BULK_DATA_INGEST_URL = '/api/iot/ingest/bulk/';
export const DEVICE_REGISTRATION_URL = '/api/iot/register/';
export const IOT_STATS_URL = '/api/iot/stats/';

// Consumer API Routes
export const QR_VERIFICATION_URL = '/api/consumer/verify/';
export const PUBLIC_ANIMAL_HISTORY_URL = (id: number) => `/api/consumer/animal/${id}/history/`;
export const GENERATE_QR_URL = (id: number) => `/api/consumer/animal/${id}/qr/`;
export const ANIMAL_SEARCH_PUBLIC_URL = '/api/consumer/search/';
export const CERTIFICATION_VERIFICATION_URL = (id: number) => `/api/consumer/certification/${id}/verify/`;
export const BLOCKCHAIN_PROOF_URL = (id: number) => `/api/consumer/animal/${id}/proof/`;
export const PUBLIC_API_DOCS_URL = '/api/consumer/docs/';

// Analytics API Routes
export const GENETIC_ANALYTICS_URL = '/api/analytics/genetic/';
export const HEALTH_TRENDS_URL = '/api/analytics/health-trends/';
export const SUPPLY_CHAIN_ANALYTICS_URL = '/api/analytics/supply-chain/';
export const SUSTAINABILITY_METRICS_URL = '/api/analytics/sustainability/';
export const BLOCKCHAIN_ANALYTICS_URL = '/api/analytics/blockchain/';
export const SYSTEM_PERFORMANCE_URL = '/api/analytics/system-performance/';
export const PREDICTIVE_ANALYTICS_URL = '/api/analytics/predictive/';
export const CUSTOM_REPORT_URL = '/api/analytics/reports/custom/';

// Market API Routes
export const MARKET_LISTINGS_URL = '/api/market/listings/';
export const TRADES_URL = '/api/market/trades/';
export const MARKET_STATS_URL = '/api/market/stats/';
export const PRICE_HISTORY_URL = '/api/market/price-history/';
export const EXECUTE_TRADE_URL = (id: number) => `/api/market/execute-trade/${id}/`;
export const ANIMAL_MARKET_URL = (id: number) => `/api/market/animal/${id}/`;

// Governance API Routes
export const GOVERNANCE_PROPOSALS_URL = '/api/governance/proposals/';
export const VOTES_URL = '/api/governance/votes/';
export const PROPOSAL_STATS_URL = '/api/governance/stats/';
export const USER_VOTING_STATS_URL = '/api/governance/user-stats/';
export const ACTIVE_PROPOSALS_URL = '/api/governance/active/';
export const PROPOSAL_TIMELINE_URL = '/api/governance/timeline/';

// Reports API Routes
export const COMPLIANCE_REPORT_URL = '/api/reports/compliance/';
export const EXPORT_ANIMAL_DATA_URL = '/api/reports/export/animals/';
export const AUDIT_REPORT_URL = '/api/reports/audit/';
export const FINANCIAL_REPORT_URL = '/api/reports/financial/';
export const SYSTEM_HEALTH_REPORT_URL = '/api/reports/system-health/';
export const EXPORT_REPORT_URL = '/api/reports/export/report/';

// Rewards API Routes
export const REWARDS_URL = '/api/rewards/rewards/';
export const STAKING_POOLS_URL = '/api/rewards/staking/';
export const REWARD_CLAIM_URL = (id: number) => `/api/rewards/claim/${id}/`;
export const BULK_REWARD_CLAIM_URL = '/api/rewards/claim/bulk/';
export const STAKE_TOKENS_URL = '/api/rewards/staking/action/stake/';
export const UNSTAKE_TOKENS_URL = (id: number) => `/api/rewards/staking/action/unstake/${id}/`;
export const REPUTATION_LEADERBOARD_URL = '/api/rewards/leaderboard/';
export const USER_REWARDS_STATS_URL = '/api/rewards/stats/';

// User Management Routes
export const USERS_URL = '/api/users/users/';
export const USER_PREFERENCES_URL = '/api/users/preferences/';
export const API_TOKENS_URL = '/api/users/api-tokens/';
export const ACTIVITY_LOGS_URL = '/api/users/activity-logs/';
export const NOTIFICATIONS_URL = '/api/users/notifications/';

// Advanced Routes
export const SMART_CONTRACT_ADMIN_URL = '/api/blockchain/advanced/contracts/admin/';
export const GAS_OPTIMIZATION_URL = '/api/blockchain/advanced/gas/optimize/';
export const DEVICE_FIRMWARE_UPDATE_URL = (id: number) => `/api/iot/advanced/firmware/${id}/`;
export const BULK_DEVICE_MANAGEMENT_URL = '/api/iot/advanced/bulk-management/';
export const IOT_NETWORK_HEALTH_URL = '/api/iot/advanced/network-health/';

// Additional API Routes
export const TRANSACTION_API_URL = '/api/transactions/';
export const AUDIT_TRAIL_EXPORT_URL = '/api/cattle/audit/export/';
export const VALIDATION_TEST_URL = '/api/core/validate/';
export const SYSTEM_MAINTENANCE_URL = '/api/core/maintenance/';
export const ERROR_TEST_URL = '/api/core/error-test/';


// constants.ts - Sección adicional para Starknet

// Starknet Sepolia
export const STARKNET_NETWORK = import.meta.env.VITE_STARKNET_NETWORK || 'alpha-sepolia';
export const STARKNET_RPC_URL = import.meta.env.VITE_STARKNET_RPC_URL || 'https://starknet-sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID';
export const STARKNET_CHAIN_ID = import.meta.env.VITE_STARKNET_CHAIN_ID || 'SN_SEPOLIA';
export const STARKNET_EXPLORER_URL = import.meta.env.VITE_STARKNET_EXPLORER_URL || 'https://sepolia.starkscan.co';

// Starknet Contract Addresses
export const STARKNET_GANADO_TOKEN_ADDRESS = import.meta.env.VITE_STARKNET_GANADO_TOKEN_ADDRESS || '0xYOUR_STARKNET_TOKEN_ADDRESS';
export const STARKNET_ANIMAL_NFT_ADDRESS = import.meta.env.VITE_STARKNET_ANIMAL_NFT_ADDRESS || '0xYOUR_STARKNET_NFT_ADDRESS';
export const STARKNET_REGISTRY_ADDRESS = import.meta.env.VITE_STARKNET_REGISTRY_ADDRESS || '0xYOUR_STARKNET_REGISTRY_ADDRESS';

// Starknet Wallet
export const STARKNET_ADMIN_WALLET_ADDRESS = import.meta.env.VITE_STARKNET_ADMIN_WALLET_ADDRESS || '0x1baaeb194649d3ec0c78942f9b462bfaf602b9a4ec84275f3d8af78ea19df2e';

// API Keys adicionales
export const STARKSCAN_API_KEY = import.meta.env.VITE_STARKSCAN_API_KEY || 'YOUR_STARKSCAN_API_KEY';
export const INFURA_PROJECT_ID = import.meta.env.VITE_INFURA_PROJECT_ID || 'YOUR_INFURA_PROJECT_ID';

// Network Configuration
export const DEFAULT_NETWORK = import.meta.env.VITE_DEFAULT_NETWORK || 'polygon-amoy';
export const SUPPORTED_NETWORKS = (import.meta.env.VITE_SUPPORTED_NETWORKS || 'polygon-amoy,alpha-sepolia').split(',');

// Feature Flags
export const ENABLE_STARKNET = import.meta.env.VITE_ENABLE_STARKNET === 'true';
export const ENABLE_MULTI_CHAIN = import.meta.env.VITE_ENABLE_MULTI_CHAIN === 'true';
export const ENABLE_IOT_INTEGRATION = import.meta.env.VITE_ENABLE_IOT_INTEGRATION !== 'false';
export const ENABLE_BLOCKCHAIN_SYNC = import.meta.env.VITE_ENABLE_BLOCKCHAIN_SYNC !== 'false';

// Starknet Provider
export const STARKNET_PROVIDER_URL = import.meta.env.VITE_STARKNET_PROVIDER_URL || 'https://starknet-sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID';