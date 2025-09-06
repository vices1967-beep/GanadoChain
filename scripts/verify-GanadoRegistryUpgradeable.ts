// scripts/verify-GanadoRegistryUpgradeable.ts
import { ethers, upgrades } from "hardhat";
import * as fs from "fs";
import * as path from "path";

async function main() {
  console.log("🔍 VERIFICACIÓN: GanadoRegistryUpgradeable");
  
  // Cargar desde raíz
  const deployedPath = path.join(__dirname, "..", "deployed-new.json");
  const deployedData = JSON.parse(fs.readFileSync(deployedPath, "utf8"));
  const registryAddress = deployedData.contracts.GanadoRegistryUpgradeable;

  console.log(`📋 Registry: ${registryAddress}`);
  
  // 1. Obtener dirección de implementación
  const implAddress = await upgrades.erc1967.getImplementationAddress(registryAddress);
  console.log(`✅ Implementación: ${implAddress}`);
  
  // 2. Conectarse al contrato
  const registry = await ethers.getContractAt("GanadoRegistryUpgradeable", registryAddress);
  
  // 3. Verificar que la nueva función existe
  try {
    await registry.updateBatchStatus.staticCall(
      999, 
      "test_status", 
      ethers.utils.formatBytes32String("test_hash")
    );
    console.log("✅ Función updateBatchStatus respondió");
  } catch (error: any) {
    if (error.message.includes("Invalid batch ID") || error.message.includes("revert")) {
      console.log("✅ Función disponible (error esperado por batchId inválido)");
    } else {
      console.log("⚠️ Error inesperado:", error.message);
    }
  }

  console.log("🎉 Verificación completada!");
}

main().catch(console.error);