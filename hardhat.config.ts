// hardhat.config.ts (en la raíz)
import { HardhatUserConfig } from "hardhat/config";
import "@nomiclabs/hardhat-ethers";
import "@nomiclabs/hardhat-etherscan";
import "@openzeppelin/hardhat-upgrades";
import "dotenv/config";

const config: HardhatUserConfig = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      }
    }
  },
  networks: {
    amoy: {
      url: process.env.RPC_URL || "",
      accounts: [
        process.env.PRIVATE_KEY!,
        process.env.PRIVATE_KEY_2!,
        process.env.PRIVATE_KEY_3!,
      ].filter(Boolean) as string[],
    },
  },
  etherscan: {
    apiKey: {
      polygonAmoy: process.env.ETHERSCAN_API_KEY!,
    }
  },
  paths: {
    sources: "./contracts",    // ✅ Desde raíz
    tests: "./test",           // ✅ Desde raíz  
    cache: "./cache",          // ✅ Desde raíz
    artifacts: "./artifacts"   // ✅ Desde raíz
  }
};

export default config;