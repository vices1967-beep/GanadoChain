import { ethers } from "ethers";
import "dotenv/config";

// RPC del archivo .env (ejemplo: https://rpc-amoy.polygon.technology)
const RPC_URL = process.env.RPC_URL as string;

// Dirección de tu Safe multisig
const safeAddress = "0x5C866fa1deC2D56f595f5B3ACAE14Bd088f0f9ee";

async function main() {
  try {
    const provider = new ethers.JsonRpcProvider(RPC_URL);

    // Consultar balance en POL
    const balance = await provider.getBalance(safeAddress);

    console.log(`📦 Safe: ${safeAddress}`);
    console.log(`💰 Balance en POL: ${ethers.formatEther(balance)} POL`);
  } catch (error) {
    console.error("❌ Error al consultar balance:", error);
  }
}

main();
