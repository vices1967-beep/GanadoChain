const { ethers } = require("hardhat");
const deployedAddresses = require("../deployed_addresses.json");

async function main() {
  console.log("==============================================");
  console.log("🚀 OPERANDO CON LA SAFE MULTISIG");
  console.log("==============================================");

  const provider = new ethers.providers.JsonRpcProvider(process.env.RPC_URL);
  
  // Tus 3 signers originales (owners de la Safe)
  const signer1 = new ethers.Wallet(process.env.PRIVATE_KEY!, provider);
  const signer2 = new ethers.Wallet(process.env.PRIVATE_KEY_2!, provider);
  const signer3 = new ethers.Wallet(process.env.PRIVATE_KEY_3!, provider);

  console.log("🔑 Owners de la Safe:");
  console.log("   Owner 1:", signer1.address);
  console.log("   Owner 2:", signer2.address);
  console.log("   Owner 3:", signer3.address);
  console.log("   Safe:", deployedAddresses.safes.deployer1);

  // Conectar a contratos usando la Safe como signer
  const TokenFactory = await ethers.getContractFactory("GanadoTokenUpgradeable", signer1);
  const NFTFactory = await ethers.getContractFactory("AnimalNFTUpgradeable", signer1);
  const RegistryFactory = await ethers.getContractFactory("GanadoRegistryUpgradeable", signer1);

  const token = TokenFactory.attach(deployedAddresses.contracts.GanadoTokenUpgradeable);
  const nft = NFTFactory.attach(deployedAddresses.contracts.AnimalNFTUpgradeable);
  const registry = RegistryFactory.attach(deployedAddresses.contracts.GanadoRegistryUpgradeable);

  // 1. PRIMERO: Dar rol ADMIN a signer1 temporalmente
  console.log("\n👑 DANDO ADMIN A SIGNER 1 TEMPORALMENTE...");
  
  const DEFAULT_ADMIN_ROLE = await token.DEFAULT_ADMIN_ROLE();
  
  try {
    // Desde la Safe necesitarías múltiples firmas, pero probemos con signer1
    const tx = await token.grantRole(DEFAULT_ADMIN_ROLE, signer1.address);
    await tx.wait();
    console.log("✅ Admin role otorgado a signer1");
  } catch (error) {
    console.log("❌ Error (normal para Safe):", error.message);
    console.log("⚠️  Necesitamos operar via la Safe multisig");
  }

  // 2. ALTERNATIVA: Operar via la Safe
  console.log("\n🎯 PARA OPERAR CON LA SAFE:");
  console.log("1. Ve a: https://app.safe.global/");
  console.log("2. Conecta con MetaMask (usando PRIVATE_KEY_1)");
  console.log("3. Añade la Safe:", deployedAddresses.safes.deployer1);
  console.log("4. Desde ahí puedes ejecutar transacciones");
}

main().catch(console.error);