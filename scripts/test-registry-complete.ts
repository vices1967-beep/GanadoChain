const { ethers } = require("hardhat");
const newAddresses = require("../deployed-new.json");

async function main() {
  console.log("==============================================");
  console.log("🚀 TESTEO COMPLETO DE REGISTRY");
  console.log("==============================================");

  const [deployer] = await ethers.getSigners();
  console.log(`🔑 Deployer: ${deployer.address}`);

  const RegistryFactory = await ethers.getContractFactory("GanadoRegistryUpgradeable");
  const NFTFactory = await ethers.getContractFactory("AnimalNFTUpgradeable");
  
  const registry = RegistryFactory.attach(newAddresses.contracts.GanadoRegistryUpgradeable);
  const nft = NFTFactory.attach(newAddresses.contracts.AnimalNFTUpgradeable);

  console.log("✅ Conectado al Registry:", registry.address);

  // 1. CREAR NFT PRIMERO
  console.log("\n🔄 CREANDO NFT PARA TEST:");
  const txMint = await nft.mintAnimal(
    deployer.address,
    "ipfs://QmTestAnimal123",
    "ipfs://QmTestOperational456"
  );
  await txMint.wait();
  console.log("   ✅ NFT creado para testing");

  // 2. TEST CREAR LOTE
  console.log("\n📦 TEST CREAR LOTE:");
  const animals = [1]; // Usar el NFT recién creado
  const loteAmount = ethers.utils.parseEther("10000");
  
  const txLote = await registry.createLote(
    deployer.address,
    loteAmount,
    "ipfs://QmLoteMetadata123",
    animals
  );
  await txLote.wait();
  console.log(`   ✅ Lote creado - TX: ${txLote.hash}`);

  // 3. VERIFICAR LOTE (CORREGIDO)
  const loteInfo = await registry.lotes(1);
  console.log(`   Lote 1 - Amount: ${ethers.utils.formatEther(loteInfo.amount)}`);
  console.log(`   Lote 1 - IPFS Hash: ${loteInfo.ipfsHash}`);
  console.log(`   Lote 1 - Animals: ${loteInfo.animals ? loteInfo.animals.length : 0}`); // ✅ Corregido

  // 4. TEST IOT DATA
  console.log("\n📡 TEST IOT DATA:");
  const txIoT = await registry.registerIoTData(
    1, // animal ID
    "device-001",
    "ipfs://QmIoTDataHash123",
    "temperature: 38.5°C, health: good"
  );
  await txIoT.wait();
  console.log("   ✅ IoT data registrado");

  // 5. VERIFICAR ROLES
  console.log("\n👑 VERIFICACIÓN DE ROLES:");
  const roles = {
    IOT: await registry.IOT_ROLE(),
    PRODUCER: await registry.PRODUCER_ROLE(),
    AUDITOR: await registry.AUDITOR_ROLE()
  };

  for (const [roleName, roleHash] of Object.entries(roles)) {
    const hasRole = await registry.hasRole(roleHash, deployer.address);
    console.log(`   ${roleName}: ${hasRole ? "✅" : "❌"} ${hasRole}`);
  }

  console.log("\n==============================================");
  console.log("🎉 TESTEO DE REGISTRY COMPLETADO EXITOSAMENTE!");
  console.log("==============================================");
}

main().catch(console.error);