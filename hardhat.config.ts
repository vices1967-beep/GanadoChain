// hardhat.config.ts
require("@nomiclabs/hardhat-ethers");
require("@nomiclabs/hardhat-etherscan");
require("@openzeppelin/hardhat-upgrades");
require("dotenv").config();

const config = {
  solidity: "0.8.20",
  networks: {
    amoy: {
      url: process.env.RPC_URL || "",
      accounts: [
        process.env.PRIVATE_KEY!,
        process.env.PRIVATE_KEY_2!,
        process.env.PRIVATE_KEY_3!,
      ],
    },
  },
  etherscan: {
    apiKey: {
      polygonAmoy: process.env.ETHERSCAN_API_KEY || "B575EDK97J1KQMVJ7PP7G2EK2QTCRYREN2",
    }
  }
};

module.exports = config;