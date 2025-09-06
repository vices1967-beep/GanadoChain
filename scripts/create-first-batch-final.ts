// scripts/create-first-batch-final.ts
import { ethers } from "hardhat";
import * as fs from "fs";
import * as path from "path";

async function main() {
  console.log("🐄 CREANDO PRIMER LOTE CON ANIMALES EXISTENTES");
  
  const deployedPath = path.join(__dirname, "..", "deployed-new.json");
  const deployedData = JSON.parse(fs.readFileSync(deployedPath, "utf8"));
  const registryAddress = deployedData.contracts.GanadoRegistryUpgradeable;

  const [deployer] = await ethers.getSigners();
  console.log(`🔑 Deployer: ${deployer.address}`);

  const registry = await ethers.getContractAt("GanadoRegistryUpgradeable", registryAddress);

  // Animales existentes (token IDs verificados)
  const animalTokenIds = [10, 11];
  const ipfsHash = "ipfs://QmPrimerLoteMetadata";
  const amount = ethers.utils.parseEther("1000");

  console.log(`📦 Creando lote con animales: ${animalTokenIds.join(", ")}`);

  // Crear el lote directamente (ya verificamos que los animales existen)
  try {
    const tx = await registry.createLote(
      deployer.address,
      amount,
      ipfsHash,
      animalTokenIds
    );

    console.log(`📋 Transacción enviada: ${tx.hash}`);
    console.log("⏳ Esperando confirmación...");
    
    const receipt = await tx.wait();
    console.log("✅ ¡Primer lote creado exitosamente!");
    console.log(`📊 Bloque: ${receipt.blockNumber}`);
    console.log(`📊 Gas usado: ${receipt.gasUsed.toString()}`);

    // Verificar el lote creado
    const loteId = await registry.nextLoteId() - 1;
    const lote = await registry.lotes(loteId);
    
    console.log(`\n🎉 LOTE CREADO:`);
    console.log(`📊 Lote ID: ${loteId}`);
    console.log(`📊 Cantidad: ${ethers.utils.formatEther(lote.amount)} tokens`);
    console.log(`📊 Estado: ${lote.status}`);
    console.log(`📊 Animales: ${lote.animals.length} animales`);
    console.log(`📊 IDs de animales: ${lote.animals.join(", ")}`);
    console.log(`📊 IPFS Hash: ${lote.ipfsHash}`);

    // Verificar que los animales fueron asignados al lote
    console.log(`\n🔍 VERIFICACIÓN DE ASIGNACIÓN:`);
    for (const tokenId of animalTokenIds) {
      const assignedLote = await registry.animalToLote(tokenId);
      console.log(`✅ Animal ${tokenId} asignado a Lote: ${assignedLote}`);
    }

  } catch (error) {
    console.log(`❌ Error creando lote: ${error.message}`);
    
    // Mostrar más detalles del error
    if (error.data) {
      console.log(`📋 Datos del error: ${error.data}`);
    }
    
    // Intentar decodificar el error
    try {
      const errorData = error.data || error.error?.data;
      if (errorData) {
        const revertReason = ethers.utils.toUtf8String(errorData.slice(138));
        console.log(`📋 Razón del revert: ${revertReason}`);
      }
    } catch (decodeError) {
      console.log("⚠️ No se pudo decodificar el error");
    }
  }
}

main().catch(console.error);