const { ethers, upgrades } = require("hardhat");

async function main() {
  console.log("==============================================");
  console.log("🚀 DESPLEGANDO CONTRATO DE TEST CON ADMIN");
  console.log("==============================================");

  const [deployer] = await ethers.getSigners();
  console.log("🔑 Deployer:", deployer.address);

  // Desplegar nuevo contrato donde deployer es admin
  const TestFactory = await ethers.getContractFactory("GanadoTokenUpgradeable");
  
  console.log("🔄 Desplegando nuevo contrato...");
  const testContract = await upgrades.deployProxy(TestFactory, [
    deployer.address, // ✅ TU address como admin
    ethers.utils.parseEther("1000000"), // initialSupply
    ethers.utils.parseEther("10000000") // cap
  ], { 
    kind: "uups",
    timeout: 120000 // 2 minutos timeout
  });

  console.log("⏳ Esperando despliegue...");
  await testContract.deployed();
  
  console.log("✅ NUEVO CONTRATO DESPLEGADO:", testContract.address);
  console.log("🎯 TÚ ERES EL ADMIN:", deployer.address);

  // Verificar
  const DEFAULT_ADMIN_ROLE = await testContract.DEFAULT_ADMIN_ROLE();
  const isAdmin = await testContract.hasRole(DEFAULT_ADMIN_ROLE, deployer.address);
  console.log("¿Eres admin?", isAdmin);
}

main().catch(console.error);