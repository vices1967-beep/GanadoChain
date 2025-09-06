// scripts/upgrade-transparent.ts
import { ethers, upgrades } from "hardhat";
import * as fs from "fs";
import * as path from "path";

async function main() {
  console.log("🔄 UPGRADE PARA TRANSPARENT PROXY");
  
  const deployedPath = path.join(__dirname, "..", "deployed-new.json");
  const deployedData = JSON.parse(fs.readFileSync(deployedPath, "utf8"));
  const registryAddress = deployedData.contracts.GanadoRegistryUpgradeable;

  const [deployer] = await ethers.getSigners();
  console.log(`🔑 Deployer: ${deployer.address}`);
  console.log(`📋 Registry: ${registryAddress}`);

  // 1. Obtener el ProxyAdmin
  const proxyAdmin = await upgrades.admin.getInstance();
  const proxyAdminAddress = await proxyAdmin.getAddress();
  console.log(`🏛️ ProxyAdmin: ${proxyAdminAddress}`);

  // 2. Verificar que el deployer es owner del ProxyAdmin
  const owner = await proxyAdmin.owner();
  console.log(`👑 ProxyAdmin Owner: ${owner}`);
  console.log(`🔍 Is deployer owner? ${owner === deployer.address}`);

  if (owner !== deployer.address) {
    console.log("❌ Deployer no es owner del ProxyAdmin");
    console.log("💡 Contacta al owner para hacer el upgrade:");
    console.log(`   Owner: ${owner}`);
    return;
  }

  // 3. Preparar el upgrade
  console.log("📦 Compilando nueva implementación...");
  const RegistryFactory = await ethers.getContractFactory("GanadoRegistryUpgradeable");
  
  // 4. Hacer el upgrade a través del ProxyAdmin
  console.log("⚡ Ejecutando upgrade...");
  const upgradeTx = await proxyAdmin.upgrade(registryAddress, await RegistryFactory.getAddress());
  console.log(`📋 Tx hash: ${upgradeTx.hash}`);
  
  // 5. Esperar confirmación
  await upgradeTx.wait();
  console.log("✅ Upgrade completado exitosamente!");

  // 6. Verificar nueva implementación
  const newImpl = await upgrades.erc1967.getImplementationAddress(registryAddress);
  console.log(`🏗️ Nueva implementación: ${newImpl}`);
}

main().catch(console.error);