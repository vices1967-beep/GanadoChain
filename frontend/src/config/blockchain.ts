export const BLOCKCHAIN_CONFIG = {
  NETWORK: {
    name: 'Polygon Amoy',
    chainId: 80002,
    rpcUrl: import.meta.env.VITE_POLYGON_RPC_URL,
    explorer: import.meta.env.VITE_BLOCK_EXPLORER,
    nativeCurrency: {
      name: 'MATIC',
      symbol: 'MATIC',
      decimals: 18,
    }
  },
  CONTRACTS: {
    CATTLE_NFT: import.meta.env.VITE_CONTRACT_ADDRESS,
  },
  GAS: {
    DEFAULT_GAS_LIMIT: 300000,
    PRIORITY_FEE: 1500000000, // 1.5 Gwei
  }
} as const

export const POLYGON_AMOY_PARAMS = {
  chainId: '0x13882', // 80002 en hexadecimal
  chainName: 'Polygon Amoy Testnet',
  nativeCurrency: {
    name: 'MATIC',
    symbol: 'MATIC',
    decimals: 18,
  },
  rpcUrls: ['https://rpc-amoy.polygon.technology'],
  blockExplorerUrls: ['https://amoy.polygonscan.com/'],
}