// scripts/upgrade-GanadoRegistryUpgradeable.ts
import { ethers, upgrades } from "hardhat";
import * as fs from "fs";
import * as path from "path";

async function main() {
  console.log("==============================================");
  console.log("🔄 UPGRADE SPECIFIC: GanadoRegistryUpgradeable");
  console.log("==============================================");

  const [deployer] = await ethers.getSigners();
  console.log(`🔑 Deployer: ${deployer.address}`);

  // Cargar direcciones desplegadas DESDE LA RAÍZ
  const deployedPath = path.join(__dirname, "..", "deployed-new.json");
  const deployedData = JSON.parse(fs.readFileSync(deployedPath, "utf8"));
  const registryAddress = deployedData.contracts.GanadoRegistryUpgradeable;

  console.log(`📋 Registry address: ${registryAddress}`);

  // 1. Compilar el nuevo contrato
  console.log("\n📦 Compilando GanadoRegistryUpgradeable...");
  const RegistryFactory = await ethers.getContractFactory("GanadoRegistryUpgradeable");
  
  // 2. Realizar el upgrade
  console.log("⚡ Realizando upgrade del Registry...");
  const upgradedRegistry = await upgrades.upgradeProxy(registryAddress, RegistryFactory);
  
  // 3. Esperar confirmación
  await upgradedRegistry.deployed();
  console.log("✅ Upgrade del Registry completado!");

  // 4. Verificar la nueva implementación
  const implAddress = await upgrades.erc1967.getImplementationAddress(registryAddress);
  console.log(`🏗️ Nueva implementación: ${implAddress}`);

  console.log("\n==============================================");
  console.log("🎉 ¡UPGRADE DE GANADOREGISTRY COMPLETADO!");
  console.log("==============================================");
}

main().catch((error) => {
  console.error("❌ Error durante el upgrade:", error);
  process.exit(1);
});