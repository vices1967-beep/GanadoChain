// scripts/create-first-batch.ts
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

  // Animales existentes (token IDs de tu backup)
  const animalTokenIds = [10, 11]; // Token IDs de tus animales
  const ipfsHash = "ipfs://QmPrimerLoteMetadata";
  const amount = ethers.utils.parseEther("1000"); // 1000 tokens

  console.log(`📦 Creando lote con animales: ${animalTokenIds.join(", ")}`);

  // Verificar que los animales existen en blockchain
  for (const tokenId of animalTokenIds) {
    try {
      const owner = await registry.nft().ownerOf(tokenId);
      console.log(`✅ Animal ${tokenId} existe, owner: ${owner}`);
    } catch (error) {
      console.log(`❌ Animal ${tokenId} no existe en blockchain: ${error.message}`);
      return;
    }
  }

  // Crear el lote
  const tx = await registry.createLote(
    deployer.address, // to
    amount,
    ipfsHash,
    animalTokenIds
  );

  console.log(`📋 Transacción enviada: ${tx.hash}`);
  await tx.wait();
  console.log("✅ ¡Primer lote creado exitosamente!");

  // Verificar el lote creado
  const loteId = await registry.nextLoteId() - 1;
  const lote = await registry.lotes(loteId);
  
  console.log(`📊 Lote ID: ${loteId}`);
  console.log(`📊 Cantidad de tokens: ${ethers.utils.formatEther(lote.amount)}`);
  console.log(`📊 Estado: ${lote.status}`);
  console.log(`📊 Animales en lote: ${lote.animals.length}`);
}

main().catch(console.error);