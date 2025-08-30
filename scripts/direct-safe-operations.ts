const { ethers } = require("hardhat");
const deployedAddresses = require("../deployed_addresses.json");

async function main() {
  console.log("==============================================");
  console.log("🚀 OPERANDO DIRECTAMENTE CON LA SAFE");
  console.log("==============================================");

  // Configurar provider
  const provider = new ethers.providers.JsonRpcProvider(process.env.RPC_URL);
  
  // Usar Owner 1 (deployer principal) - PRIVATE_KEY del .env
  const owner1 = new ethers.Wallet(process.env.PRIVATE_KEY!, provider);
  
  console.log("🔑 Operando con Owner 1:", owner1.address);
  console.log("🏦 Safe Address:", deployedAddresses.safes.deployer1);
  console.log("🗝️ Token Address:", deployedAddresses.contracts.GanadoTokenUpgradeable);

  // Conectar al contrato Token
  const TokenFactory = await ethers.getContractFactory("GanadoTokenUpgradeable", owner1);
  const token = TokenFactory.attach(deployedAddresses.contracts.GanadoTokenUpgradeable);

  // Intentar asignar rol DAO a Owner 1
  try {
    const DAO_ROLE = await token.DAO_ROLE();
    console.log("🔍 Intentando asignar DAO_ROLE...");
    
    const tx = await token.grantRole(DAO_ROLE, owner1.address);
    console.log("✅ Transacción enviada:", tx.hash);
    
    await tx.wait();
    console.log("🎉 Rol DAO asignado correctamente!");
    
    // Verificar
    const hasRole = await token.hasRole(DAO_ROLE, owner1.address);
    console.log("¿Owner 1 tiene rol DAO?", hasRole);
    
  } catch (error) {
    console.log("❌ Error (probablemente necesita múltiples firmas):");
    console.log("   ", error.message);
    console.log("💡 Usa el script de nuevo contrato para testing inmediato");
  }
}

main().catch(console.error);