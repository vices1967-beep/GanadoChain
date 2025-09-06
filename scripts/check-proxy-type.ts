// scripts/check-proxy-type.ts
import { ethers, upgrades } from "hardhat";
import * as fs from "fs";
import * as path from "path";

async function main() {
  const deployedPath = path.join(__dirname, "..", "deployed-new.json");
  const deployedData = JSON.parse(fs.readFileSync(deployedPath, "utf8"));
  const registryAddress = deployedData.contracts.GanadoRegistryUpgradeable;

  console.log("🔍 Verificando tipo de proxy...");
  console.log(`📋 Address: ${registryAddress}`);

  try {
    // Intentar detectar el tipo de proxy
    const implAddress = await upgrades.erc1967.getImplementationAddress(registryAddress);
    console.log(`✅ Implementation address: ${implAddress}`);
    
    // Verificar si es UUPS
    const registry = await ethers.getContractAt("GanadoRegistryUpgradeable", registryAddress);
    
    // Check if has UUPS functions
    try {
      await registry.proxiableUUID();
      console.log("🎯 Tipo de proxy: UUPS");
    } catch {
      console.log("🎯 Tipo de proxy: Transparent");
    }
    
  } catch (error) {
    console.log("❌ No se pudo determinar el tipo de proxy:", error);
  }
}

main().catch(console.error);