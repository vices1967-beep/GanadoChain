/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_APP_NAME: string
  readonly VITE_APP_VERSION: string
  readonly VITE_API_BASE_URL: string
  readonly VITE_API_TIMEOUT: string
  readonly VITE_JWT_ACCESS_TOKEN_KEY: string
  readonly VITE_JWT_REFRESH_TOKEN_KEY: string
  readonly VITE_LOGIN_URL: string
  readonly VITE_REFRESH_TOKEN_URL: string
  readonly VITE_REGISTER_URL: string
  readonly VITE_WALLET_CONNECT_URL: string
  readonly VITE_BLOCKCHAIN_RPC_URL: string
  readonly VITE_CHAIN_ID: string
  // ... otras variables de entorno
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}