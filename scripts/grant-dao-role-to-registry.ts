// scripts/grant-dao-role-to-registry.ts
const { ethers } = require("hardhat");
const newAddresses = require("../deployed-new.json");

async function main() {
  console.log("==============================================");
  console.log("🚀 OTORGANDO DAO_ROLE AL REGISTRY");
  console.log("==============================================");

  const [deployer] = await ethers.getSigners();
  
  const TokenFactory = await ethers.getContractFactory("GanadoTokenUpgradeable");
  const token = TokenFactory.attach(newAddresses.contracts.GanadoTokenUpgradeable);

  // Obtener DAO_ROLE (el que realmente necesita)
  const DAO_ROLE = await token.DAO_ROLE();
  
  console.log("🔍 Verificando DAO_ROLE actual...");
  const hasDAORole = await token.hasRole(DAO_ROLE, newAddresses.contracts.GanadoRegistryUpgradeable);
  console.log(`   Registry tiene DAO_ROLE: ${hasDAORole}`);

  if (!hasDAORole) {
    console.log("🎯 Otorgando DAO_ROLE al Registry...");
    const tx = await token.grantRole(DAO_ROLE, newAddresses.contracts.GanadoRegistryUpgradeable);
    await tx.wait();
    console.log("✅ DAO_ROLE otorgado al Registry");
    
    // Verificar
    const nowHasRole = await token.hasRole(DAO_ROLE, newAddresses.contracts.GanadoRegistryUpgradeable);
    console.log(`   Ahora Registry tiene DAO_ROLE: ${nowHasRole}`);
  } else {
    console.log("✅ El Registry ya tiene DAO_ROLE");
  }

  console.log("\n==============================================");
  console.log("🎉 DAO_ROLE CONFIGURADO CORRECTAMENTE!");
  console.log("==============================================");
}

main().catch(console.error);