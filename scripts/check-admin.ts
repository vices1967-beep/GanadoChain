const { ethers } = require("hardhat");
const deployedAddresses = require("../deployed_addresses.json");

async function main() {
  console.log("==============================================");
  console.log("🔍 VERIFICANDO ADMINS ACTUALES");
  console.log("==============================================");

  const [deployer] = await ethers.getSigners();
  
  // Conectar a contratos
  const TokenFactory = await ethers.getContractFactory("GanadoTokenUpgradeable");
  const NFTFactory = await ethers.getContractFactory("AnimalNFTUpgradeable");
  const RegistryFactory = await ethers.getContractFactory("GanadoRegistryUpgradeable");

  const token = TokenFactory.attach(deployedAddresses.contracts.GanadoTokenUpgradeable);
  const nft = NFTFactory.attach(deployedAddresses.contracts.AnimalNFTUpgradeable);
  const registry = RegistryFactory.attach(deployedAddresses.contracts.GanadoRegistryUpgradeable);

  // Obtener DEFAULT_ADMIN_ROLE
  const DEFAULT_ADMIN_ROLE = await token.DEFAULT_ADMIN_ROLE();

  // Verificar admins
  console.log("\n👑 ADMINS ACTUALES:");
  
  const tokenAdmin = await token.hasRole(DEFAULT_ADMIN_ROLE, deployedAddresses.safes.deployer1);
  console.log(`   Token Admin (Safe): ${tokenAdmin} - ${deployedAddresses.safes.deployer1}`);
  
  const nftAdmin = await nft.hasRole(DEFAULT_ADMIN_ROLE, deployedAddresses.safes.deployer1);
  console.log(`   NFT Admin (Safe): ${nftAdmin} - ${deployedAddresses.safes.deployer1}`);
  
  const registryAdmin = await registry.hasRole(DEFAULT_ADMIN_ROLE, deployedAddresses.safes.deployer1);
  console.log(`   Registry Admin (Safe): ${registryAdmin} - ${deployedAddresses.safes.deployer1}`);

  // Verificar si deployer tiene algún rol
  console.log("\n🔍 ROLES DEL DEPLOYER:");
  console.log(`   Deployer: ${deployer.address}`);
  console.log(`   Token Admin: ${await token.hasRole(DEFAULT_ADMIN_ROLE, deployer.address)}`);
  console.log(`   NFT Admin: ${await nft.hasRole(DEFAULT_ADMIN_ROLE, deployer.address)}`);
  console.log(`   Registry Admin: ${await registry.hasRole(DEFAULT_ADMIN_ROLE, deployer.address)}`);

  console.log("\n==============================================");
  console.log("🎉 VERIFICACIÓN COMPLETADA");
  console.log("==============================================");
}

main().catch(console.error);