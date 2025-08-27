import 'dotenv/config';
import { ethers } from 'ethers';

// Variables de entorno
const RPC_URL = process.env.RPC_URL as string;
const PRIVATE_KEY = process.env.PRIVATE_KEY as string;
const SAFE_ADDRESS = "0x5C866fa1deC2D56f595f5B3ACAE14Bd088f0f9ee"; // tu Safe
const AMOUNT_POL = "0.1"; // cantidad a enviar en POL

// Inicializar provider y signer
const provider = new ethers.JsonRpcProvider(RPC_URL);
const signer = new ethers.Wallet(PRIVATE_KEY, provider);

async function main() {
  const tx = await signer.sendTransaction({
    to: SAFE_ADDRESS,
    value: ethers.parseEther(AMOUNT_POL),
  });

  console.log("Transacción enviada. Hash:", tx.hash);
  const receipt = await tx.wait();
  console.log("Transacción confirmada en bloque:", receipt.blockNumber);
}

main().catch(console.error);
