import 'dotenv/config';
import { ethers } from 'ethers';
import { SafeFactory, EthersAdapter } from '@safe-global/protocol-kit';

const RPC_URL = process.env.RPC_URL as string;
const PRIVATE_KEY = process.env.PRIVATE_KEY as string;

const provider = new ethers.JsonRpcProvider(RPC_URL);
const signer = new ethers.Wallet(PRIVATE_KEY, provider);

const ethAdapter = new EthersAdapter({ ethers, signerOrProvider: signer });

const owners = [signer.address];
const threshold = 1;
const saltNonce = Date.now().toString(); // <-- convertir a string

async function main() {
  const safeFactory = await SafeFactory.create({ ethAdapter });

  const safeAccountConfig = { owners, threshold };

  const safe = await safeFactory.deploySafe({
    safeAccountConfig,
    saltNonce, // ahora sí es string
  });

  console.log('✅ Safe desplegado en:', await safe.getAddress());
}

main();
