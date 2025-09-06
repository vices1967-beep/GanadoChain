// scripts/upgrade-direct.ts
import { ethers } from "hardhat";
import * as fs from "fs";
import * as path from "path";

async function main() {
  console.log("🔄 UPGRADE DIRECTO (ERES ADMIN)");
  
  const deployedPath = path.join(__dirname, "..", "deployed-new.json");
  const deployedData = JSON.parse(fs.readFileSync(deployedPath, "utf8"));
  const registryAddress = deployedData.contracts.GanadoRegistryUpgradeable;

  const [deployer] = await ethers.getSigners();
  console.log(`🔑 Deployer: ${deployer.address}`);
  console.log(`📋 Registry: ${registryAddress}`);

  // 1. Compilar nueva implementación
  console.log("📦 Compilando nueva versión...");
  const RegistryFactory = await ethers.getContractFactory("GanadoRegistryUpgradeable");
  const newImpl = await RegistryFactory.deploy();
  await newImpl.deployed();
  console.log(`✅ Nueva implementación: ${newImpl.address}`);

  // 2. Conectar al contrato existente
  const registry = await ethers.getContractAt("GanadoRegistryUpgradeable", registryAddress);
  
  // 3. Verificar que tenemos permisos de upgrade
  console.log("🔍 Verificando permisos...");
  try {
    const hasRole = await registry.hasRole(ethers.utils.keccak256(ethers.utils.toUtf8Bytes("UPGRADER_ROLE")), deployer.address);
    console.log(`✅ Tienes rol UPGRADER: ${hasRole}`);
  } catch (error) {
    console.log("⚠️ No se pudo verificar rol:", error.message);
  }

  // 4. Ejecutar upgrade directamente
  console.log("⚡ Ejecutando upgrade directo...");
  try {
    const upgradeTx = await registry.upgradeTo(newImpl.address);
    console.log(`📋 Tx hash: ${upgradeTx.hash}`);
    
    console.log("⏳ Esperando confirmación...");
    await upgradeTx.wait();
    console.log("✅ ¡Upgrade completado exitosamente!");
    
    // 5. Verificar nueva implementación
    const newImplAddress = await ethers.provider.getStorageAt(
      registryAddress,
      "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc"
    );
    const formattedImpl = ethers.utils.getAddress("0x" + newImplAddress.slice(26));
    console.log(`🏗️ Nueva implementación verificada: ${formattedImpl}`);
    
  } catch (error) {
    console.log("❌ Error en upgrade:", error.message);
    console.log("💡 Intentando método alternativo...");
    
    // Método alternativo: llamar upgradeTo directamente
    const upgradeData = registry.interface.encodeFunctionData("upgradeTo", [newImpl.address]);
    console.log(`📋 Datos de transacción: ${upgradeData}`);
    
    const tx = await deployer.sendTransaction({
      to: registryAddress,
      data: upgradeData,
      gasLimit: 1000000
    });
    
    console.log(`📋 Tx hash alternativo: ${tx.hash}`);
    await tx.wait();
    console.log("✅ ¡Upgrade completado con método alternativo!");
  }
}

main().catch(console.error);