import { ethers } from "hardhat";

// ---------------------------
// Función para calcular dirección de contrato (Ethers v6 compatible)
// ---------------------------
function computeAddress(deployer: string, nonce: number) {
  const encoded = ethers.AbiCoder.defaultAbiCoder().encode(
    ["address", "uint256"],
    [deployer, nonce]
  );
  const hash = ethers.keccak256(encoded);
  return "0x" + hash.slice(-40);
}

async function main() {
  console.log("==============================================");
  console.log("🚀 GANADOCHAIN DRY-RUN DEPLOY SCRIPT");
  console.log("==============================================");

  const RPC_URL = process.env.RPC_URL!;
  const PRIVATE_KEYS = [
    process.env.PRIVATE_KEY!,
    process.env.PRIVATE_KEY_2!,
    process.env.PRIVATE_KEY_3!
  ];

  if (!RPC_URL || PRIVATE_KEYS.some(k => !k)) {
    throw new Error("⚠️ Faltan PRIVATE_KEY o RPC_URL en .env");
  }

  const provider = new ethers.JsonRpcProvider(RPC_URL);
  const deployers = PRIVATE_KEYS.map(k => new ethers.Wallet(k, provider));

  for (let i = 0; i < deployers.length; i++) {
    const deployer = deployers[i];
    console.log("----------------------------------------------");
    console.log(`Deployer ${i + 1} address:`, deployer.address);
    const balance = await provider.getBalance(deployer.address);
    console.log("Saldo:", ethers.formatEther(balance), "POL");
  }

  console.log("----------------------------------------------");
  console.log("Simulando despliegue de contratos...");

  const contracts = [
    "GanadoTokenUpgradeable",
    "AnimalNFTUpgradeable",
    "GanadoRegistryUpgradeable",
  ];

  for (const name of contracts) {
    const factory = await ethers.getContractFactory(name, deployers[0]);
    const deployTx = await factory.getDeployTransaction();
    console.log(`${name} tx preparada:`, deployTx);
  }

  console.log("----------------------------------------------");
  console.log("✅ Dry-run completado. Ninguna transacción fue enviada.");

  console.log("----------------------------------------------");
  for (let i = 0; i < deployers.length; i++) {
    const deployer = deployers[i];
    const nonce = await provider.getTransactionCount(deployer.address);
    const safePredicted = computeAddress(deployer.address, nonce);
    console.log(`Safe address prevista deployer ${i + 1}:`, safePredicted);
  }

  console.log("----------------------------------------------");
  console.log("🏁 Dry-run finalizado correctamente.");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Error en dry-run:", error);
    process.exit(1);
  });
