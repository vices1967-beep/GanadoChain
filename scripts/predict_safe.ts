import 'dotenv/config';
import { ethers } from 'ethers';
import { SafeFactory, EthersAdapter } from '@safe-global/protocol-kit';

const RPC_URL = process.env.RPC_URL!;
const PRIVATE_KEY = process.env.PRIVATE_KEY!;

const provider = new ethers.JsonRpcProvider(RPC_URL);
const signer = new ethers.Wallet(PRIVATE_KEY, provider);

const ethAdapter = new EthersAdapter({
  ethers,
  signerOrProvider: signer,
});

async function main() {
  const safeFactory = await SafeFactory.create({ ethAdapter });

  const owners = ['0xF27c409539AC5a5deB6fe0FCac5434AD9867B310'];
  const threshold = 1;
  const saltNonce = '12345'; // string

  const predictedSafeAddress = await safeFactory.predictSafeAddress(
    { owners, threshold },
    saltNonce
  );

  console.log('Dirección prevista del Safe en Amoy:', predictedSafeAddress);

  const code = await provider.getCode(predictedSafeAddress);
  if (code && code !== '0x') {
    console.log('✅ Este Safe ya existe en la blockchain');
  } else {
    console.log('⚠️ Este Safe aún no existe. Puedes desplegarlo.');
  }
}

main().catch(console.error);
