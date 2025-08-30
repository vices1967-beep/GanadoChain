const { ethers, upgrades } = require("hardhat");
const fs = require("fs");

async function main() {
  console.log("==============================================");
  console.log("🚀 RE-DEPLOY COMPLETO CON ADMIN PERSONAL");
  console.log("==============================================");

  const [deployer] = await ethers.getSigners();
  console.log(`🔑 Deployer: ${deployer.address}`);

  const initialSupply = ethers.utils.parseEther("1000000");
  const cap = ethers.utils.parseEther("10000000");

  // 1. DEPLOY GANADO TOKEN (con deployer como admin)
  console.log("\n🔄 Desplegando GanadoTokenUpgradeable...");
  const TokenFactory = await ethers.getContractFactory("GanadoTokenUpgradeable");
  const token = await upgrades.deployProxy(TokenFactory, [
    deployer.address, // ✅ TU address como admin
    initialSupply,
    cap
  ], { kind: "uups" });
  await token.deployed();
  console.log("✅ Token deployed:", token.address);

  // 2. DEPLOY ANIMAL NFT (con deployer como admin)
  console.log("\n🔄 Desplegando AnimalNFTUpgradeable...");
  const NFTFactory = await ethers.getContractFactory("AnimalNFTUpgradeable");
  const nft = await upgrades.deployProxy(NFTFactory, [
    deployer.address // ✅ TU address como admin
  ], { kind: "uups" });
  await nft.deployed();
  console.log("✅ NFT deployed:", nft.address);

  // 3. DEPLOY REGISTRY (con deployer como admin)
  console.log("\n🔄 Desplegando GanadoRegistryUpgradeable...");
  const RegistryFactory = await ethers.getContractFactory("GanadoRegistryUpgradeable");
  const registry = await upgrades.deployProxy(RegistryFactory, [
    deployer.address, // ✅ TU address como admin
    token.address,
    nft.address
  ], { kind: "uups" });
  await registry.deployed();
  console.log("✅ Registry deployed:", registry.address);

  // 4. GUARDAR NUEVAS DIRECCIONES
  const deployed = {
    network: "polygon-amoy",
    contracts: {
      GanadoTokenUpgradeable: token.address,
      AnimalNFTUpgradeable: nft.address,
      GanadoRegistryUpgradeable: registry.address
    }
  };

  fs.writeFileSync("deployed-new.json", JSON.stringify(deployed, null, 2));
  console.log("\n📁 Nuevas direcciones guardadas en deployed-new.json");

  console.log("\n==============================================");
  console.log("🎉 ¡RE-DEPLOY COMPLETADO!");
  console.log("🎯 ¡AHORA ERES ADMIN DE TODOS LOS CONTRATOS!");
  console.log("==============================================");
}

main().catch(console.error);