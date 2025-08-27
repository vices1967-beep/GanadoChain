// check_balance.ts
import 'dotenv/config';
import { ethers } from 'ethers';

const RPC_URL = process.env.RPC_URL as string;
const PRIVATE_KEY = process.env.PRIVATE_KEY as string;

async function main() {
  const provider = new ethers.JsonRpcProvider(RPC_URL);
  const wallet = new ethers.Wallet(PRIVATE_KEY, provider);

  const balance = await provider.getBalance(wallet.address);
  console.log(`Dirección: ${wallet.address}`);
  console.log(`Saldo: ${ethers.formatEther(balance)} POL`);
}

main().catch(console.error);
