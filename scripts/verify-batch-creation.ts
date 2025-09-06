// scripts/verify-batch-creation.ts
import { ethers } from "hardhat";
import * as fs from "fs";
import * as path from "path";

async function main() {
  console.log("🔍 VERIFICACIÓN COMPLETA DEL LOTE CREADO");
  
  const deployedPath = path.join(__dirname, "..", "deployed-new.json");
  const deployedData = JSON.parse(fs.readFileSync(deployedPath, "utf8"));
  const registryAddress = deployedData.contracts.GanadoRegistryUpgradeable;

  const [deployer] = await ethers.getSigners();
  const registry = await ethers.getContractAt("GanadoRegistryUpgradeable", registryAddress);

  // Verificar lote 3 (el recién creado)
  console.log("📦 VERIFICANDO LOTE 3:");
  try {
    const lote = await registry.lotes(3);
    
    console.log(`✅ Lote ID: ${lote.loteId}`);
    console.log(`✅ IPFS Hash: ${lote.ipfsHash}`);
    console.log(`✅ Cantidad: ${ethers.utils.formatEther(lote.amount)} tokens`);
    console.log(`✅ Estado: ${lote.status}`);
    console.log(`✅ Número de animales: ${lote.animals.length}`);
    
    // Mostrar IDs de animales de manera segura
    if (lote.animals && lote.animals.length > 0) {
      console.log(`✅ IDs de animales: ${lote.animals.join(", ")}`);
    } else {
      console.log("⚠️ No se pudieron obtener los animales del lote");
    }
    
  } catch (error) {
    console.log(`❌ Error accediendo al lote 3: ${error.message}`);
  }

  // Verificar asignación de animales a lote
  console.log("\n🔍 VERIFICANDO ASIGNACIÓN DE ANIMALES:");
  const animalTokenIds = [10, 11];
  
  for (const tokenId of animalTokenIds) {
    try {
      const loteId = await registry.animalToLote(tokenId);
      console.log(`✅ Animal ${tokenId} asignado a Lote: ${loteId}`);
    } catch (error) {
      console.log(`❌ Error verificando animal ${tokenId}: ${error.message}`);
    }
  }

  // Verificar nextLoteId
  console.log("\n🔍 VERIFICANDO ESTADO GENERAL:");
  try {
    const nextLoteId = await registry.nextLoteId();
    console.log(`✅ nextLoteId: ${nextLoteId} (próximo lote será ID ${nextLoteId})`);
    
    // Verificar todos los lotes existentes
    console.log(`\n📊 LOTES EXISTENTES:`);
    for (let i = 1; i < nextLoteId; i++) {
      try {
        const lote = await registry.lotes(i);
        console.log(`   Lote ${i}: ${lote.animals?.length || 0} animales, Estado: ${lote.status}`);
      } catch (error) {
        console.log(`   Lote ${i}: Error al acceder`);
      }
    }
  } catch (error) {
    console.log(`❌ Error verificando nextLoteId: ${error.message}`);
  }

  console.log("\n🎉 VERIFICACIÓN COMPLETADA!");
}

main().catch(console.error);