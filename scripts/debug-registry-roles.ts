// scripts/debug-registry-roles.ts
const { ethers } = require("hardhat");
const newAddresses = require("../deployed-new.json");

async function main() {
  console.log("==============================================");
  console.log("🔍 DEBUG DETALLADO DE ROLES DEL REGISTRY");
  console.log("==============================================");

  const [deployer] = await ethers.getSigners();
  
  const TokenFactory = await ethers.getContractFactory("GanadoTokenUpgradeable");
  const token = TokenFactory.attach(newAddresses.contracts.GanadoTokenUpgradeable);

  // Obtener todos los roles posibles
  const roles = {
    DAO_ROLE: await token.DAO_ROLE(),
    MINTER_ROLE: await token.MINTER_ROLE(),
    PAUSER_ROLE: await token.PAUSER_ROLE(),
    UPGRADER_ROLE: await token.UPGRADER_ROLE()
  };

  console.log("📊 ROLES EN TOKEN:");
  for (const [roleName, roleHash] of Object.entries(roles)) {
    const hasRole = await token.hasRole(roleHash, newAddresses.contracts.GanadoRegistryUpgradeable);
    console.log(`   ${roleName}: ${hasRole} (${roleHash})`);
  }

  // Verificar también el DEFAULT_ADMIN_ROLE
  const DEFAULT_ADMIN_ROLE = await token.DEFAULT_ADMIN_ROLE();
  const isAdmin = await token.hasRole(DEFAULT_ADMIN_ROLE, newAddresses.contracts.GanadoRegistryUpgradeable);
  console.log(`   DEFAULT_ADMIN_ROLE: ${isAdmin} (${DEFAULT_ADMIN_ROLE})`);

  console.log("\n👑 ROLES DEL DEPLOYER:");
  for (const [roleName, roleHash] of Object.entries(roles)) {
    const hasRole = await token.hasRole(roleHash, deployer.address);
    console.log(`   ${roleName}: ${hasRole}`);
  }
}

main().catch(console.error);