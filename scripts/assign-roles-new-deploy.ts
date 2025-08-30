// scripts/assign-roles-new-deploy.ts
const { ethers } = require("hardhat");
const newAddresses = require("../deployed-new.json");

async function main() {
  console.log("==============================================");
  console.log("🚀 ASIGNANDO ROLES A NUEVOS CONTRATOS");
  console.log("==============================================");

  const [deployer] = await ethers.getSigners();
  console.log(`🔑 Deployer: ${deployer.address}`);

  // Conectar a los NUEVOS contratos
  const TokenFactory = await ethers.getContractFactory("GanadoTokenUpgradeable");
  const NFTFactory = await ethers.getContractFactory("AnimalNFTUpgradeable");
  const RegistryFactory = await ethers.getContractFactory("GanadoRegistryUpgradeable");

  const token = TokenFactory.attach(newAddresses.contracts.GanadoTokenUpgradeable);
  const nft = NFTFactory.attach(newAddresses.contracts.AnimalNFTUpgradeable);
  const registry = RegistryFactory.attach(newAddresses.contracts.GanadoRegistryUpgradeable);

  console.log("✅ Conectado a NUEVOS contratos:");
  console.log("   Token:", newAddresses.contracts.GanadoTokenUpgradeable);
  console.log("   NFT:", newAddresses.contracts.AnimalNFTUpgradeable);
  console.log("   Registry:", newAddresses.contracts.GanadoRegistryUpgradeable);

  // Verificar que somos admin en los nuevos contratos
  const DEFAULT_ADMIN_ROLE = await token.DEFAULT_ADMIN_ROLE();
  
  const isAdminToken = await token.hasRole(DEFAULT_ADMIN_ROLE, deployer.address);
  const isAdminNFT = await nft.hasRole(DEFAULT_ADMIN_ROLE, deployer.address);
  const isAdminRegistry = await registry.hasRole(DEFAULT_ADMIN_ROLE, deployer.address);

  console.log("\n👑 VERIFICANDO ADMIN EN NUEVOS CONTRATOS:");
  console.log(`   Token: ${isAdminToken}`);
  console.log(`   NFT: ${isAdminNFT}`);
  console.log(`   Registry: ${isAdminRegistry}`);

  // Solo continuar si somos admin en todos
  if (isAdminToken && isAdminNFT && isAdminRegistry) {
    console.log("\n🎯 ASIGNANDO ROLES...");
    // Aquí el código para asignar todos los roles
  } else {
    console.log("\n❌ No eres admin en todos los nuevos contratos");
    console.log("   Ejecuta el deploy nuevamente o verifica las direcciones");
  }
}

main().catch(console.error);