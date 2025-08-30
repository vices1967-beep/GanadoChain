const { ethers } = require("hardhat");
const newAddresses = require("../deployed-new.json");

async function main() {
  console.log("==============================================");
  console.log("🚀 OTORGANDO PERMISOS AL REGISTRY");
  console.log("==============================================");

  const [deployer] = await ethers.getSigners();
  console.log(`🔑 Deployer: ${deployer.address}`);

  // Conectar a los contratos
  const TokenFactory = await ethers.getContractFactory("GanadoTokenUpgradeable");
  const RegistryFactory = await ethers.getContractFactory("GanadoRegistryUpgradeable");

  const token = TokenFactory.attach(newAddresses.contracts.GanadoTokenUpgradeable);
  const registry = RegistryFactory.attach(newAddresses.contracts.GanadoRegistryUpgradeable);

  console.log("✅ Contratos conectados:");
  console.log("   Token:", token.address);
  console.log("   Registry:", registry.address);

  // 1. Obtener el rol MINTER_ROLE
  const MINTER_ROLE = await token.MINTER_ROLE();
  
  // 2. Verificar si el Registry ya tiene el rol
  const hasRole = await token.hasRole(MINTER_ROLE, registry.address);
  console.log(`📊 Registry tiene MINTER_ROLE: ${hasRole}`);

  if (!hasRole) {
    console.log("🎯 Otorgando MINTER_ROLE al Registry...");
    
    // 3. Otorgar el rol MINTER_ROLE al contrato Registry
    const tx = await token.grantRole(MINTER_ROLE, registry.address);
    await tx.wait();
    console.log("✅ MINTER_ROLE otorgado al Registry");
    
    // 4. Verificar nuevamente
    const nowHasRole = await token.hasRole(MINTER_ROLE, registry.address);
    console.log(`📊 Ahora Registry tiene MINTER_ROLE: ${nowHasRole}`);
  } else {
    console.log("✅ El Registry ya tiene MINTER_ROLE");
  }

  console.log("\n==============================================");
  console.log("🎉 PERMISOS CONFIGURADOS CORRECTAMENTE!");
  console.log("==============================================");
  console.log("📍 Ahora el Registry puede crear lotes y mintear tokens");
  console.log("📍 Ejecuta test-registry-complete.ts nuevamente");
  console.log("==============================================");
}

main().catch(console.error);