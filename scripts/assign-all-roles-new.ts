const { ethers } = require("hardhat");
const newAddresses = require("../deployed-new.json");

async function main() {
  console.log("==============================================");
  console.log("🚀 ASIGNANDO TODOS LOS ROLES - NUEVOS CONTRATOS");
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

  console.log("\n👑 VERIFICANDO ADMIN:");
  console.log(`   Token: ${isAdminToken}`);
  console.log(`   NFT: ${isAdminNFT}`);
  console.log(`   Registry: ${isAdminRegistry}`);

  if (!isAdminToken || !isAdminNFT || !isAdminRegistry) {
    console.log("❌ No eres admin en todos los contratos");
    return;
  }

  console.log("\n🎯 ASIGNANDO TODOS LOS ROLES...");

  // Todos los roles a asignar
  const rolesToAssign = [
    // Token roles
    { contract: token, role: await token.DAO_ROLE(), name: "DAO_ROLE (Token)" },
    { contract: token, role: await token.MINTER_ROLE(), name: "MINTER_ROLE (Token)" },
    { contract: token, role: await token.PAUSER_ROLE(), name: "PAUSER_ROLE (Token)" },
    { contract: token, role: await token.UPGRADER_ROLE(), name: "UPGRADER_ROLE (Token)" },

    // NFT roles
    { contract: nft, role: await nft.PRODUCER_ROLE(), name: "PRODUCER_ROLE (NFT)" },
    { contract: nft, role: await nft.VET_ROLE(), name: "VET_ROLE (NFT)" },
    { contract: nft, role: await nft.FRIGORIFICO_ROLE(), name: "FRIGORIFICO_ROLE (NFT)" },
    { contract: nft, role: await nft.AUDITOR_ROLE(), name: "AUDITOR_ROLE (NFT)" },
    { contract: nft, role: await nft.PAUSER_ROLE(), name: "PAUSER_ROLE (NFT)" },
    { contract: nft, role: await nft.UPGRADER_ROLE(), name: "UPGRADER_ROLE (NFT)" },

    // Registry roles
    { contract: registry, role: await registry.DAO_ROLE(), name: "DAO_ROLE (Registry)" },
    { contract: registry, role: await registry.UPGRADER_ROLE(), name: "UPGRADER_ROLE (Registry)" },
    { contract: registry, role: await registry.PRODUCER_ROLE(), name: "PRODUCER_ROLE (Registry)" },
    { contract: registry, role: await registry.VET_ROLE(), name: "VET_ROLE (Registry)" },
    { contract: registry, role: await registry.FRIGORIFICO_ROLE(), name: "FRIGORIFICO_ROLE (Registry)" },
    { contract: registry, role: await registry.AUDITOR_ROLE(), name: "AUDITOR_ROLE (Registry)" },
    { contract: registry, role: await registry.IOT_ROLE(), name: "IOT_ROLE (Registry)" }
  ];

  // Asignar todos los roles
  for (const { contract, role, name } of rolesToAssign) {
    try {
      const hasRoleAlready = await contract.hasRole(role, deployer.address);
      
      if (!hasRoleAlready) {
        console.log(`   ⌛ Asignando ${name}...`);
        const tx = await contract.grantRole(role, deployer.address);
        await tx.wait();
        console.log(`   ✅ ${name} asignado`);
      } else {
        console.log(`   ⏩ ${name} ya estaba asignado`);
      }
      
    } catch (error) {
      console.log(`   ❌ Error en ${name}: ${error.message}`);
    }
  }

  console.log("\n🔍 VERIFICANDO TODOS LOS ROLES...");
  
  // Verificar todos los roles
  for (const { contract, role, name } of rolesToAssign) {
    const hasRole = await contract.hasRole(role, deployer.address);
    console.log(`   ${name}: ${hasRole ? "✅" : "❌"} ${hasRole}`);
  }

  console.log("\n==============================================");
  console.log("🎉 ¡TODOS LOS ROLES ASIGNADOS EXITOSAMENTE!");
  console.log("==============================================");
  console.log("📍 Ahora puedes probar TODAS las funcionalidades");
  console.log("📍 Ejecuta scripts de interacción completos");
  console.log("==============================================");
}

main().catch(console.error);