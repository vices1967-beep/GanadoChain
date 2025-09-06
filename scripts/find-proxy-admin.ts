// scripts/find-proxy-admin.ts
import { ethers } from "hardhat";
import * as fs from "fs";
import * as path from "path";

async function main() {
  console.log("🔍 BUSCANDO PROXYADMIN");
  
  const deployedPath = path.join(__dirname, "..", "deployed-new.json");
  const deployedData = JSON.parse(fs.readFileSync(deployedPath, "utf8"));
  const registryAddress = deployedData.contracts.GanadoRegistryUpgradeable;

  const [deployer] = await ethers.getSigners();
  console.log(`🔑 Deployer: ${deployer.address}`);
  console.log(`📋 Registry: ${registryAddress}`);

  // 1. El ProxyAdmin suele estar en una dirección predecible para Transparent Proxies
  // Podemos intentar varias estrategias para encontrarlo

  // Estrategia 1: Usar el slot de storage del admin
  console.log("\n🔎 Buscando ProxyAdmin via storage slot...");
  
  // Slot para ProxyAdmin en Transparent Proxy
  const ADMIN_SLOT = "0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103";
  
  try {
    const adminAddress = await ethers.provider.getStorage(registryAddress, ADMIN_SLOT);
    const formattedAdmin = ethers.utils.getAddress("0x" + adminAddress.slice(26));
    console.log(`✅ ProxyAdmin encontrado: ${formattedAdmin}`);
    
    // Verificar si es un contrato válido
    const code = await ethers.provider.getCode(formattedAdmin);
    if (code !== "0x") {
      console.log(`📋 Es un contrato: Sí`);
      
      // Crear instancia y verificar owner
      const ProxyAdminABI = [
        "function owner() view returns (address)",
        "function getProxyAdmin(address proxy) view returns (address)",
        "function upgrade(address proxy, address implementation) external"
      ];
      
      const proxyAdmin = new ethers.Contract(formattedAdmin, ProxyAdminABI, deployer);
      
      try {
        const owner = await proxyAdmin.owner();
        console.log(`👑 Owner del ProxyAdmin: ${owner}`);
        console.log(`🔍 Eres owner? ${owner === deployer.address}`);
      } catch (e) {
        console.log("⚠️ No se pudo obtener owner:", e.message);
      }
    } else {
      console.log("❌ No es un contrato válido");
    }
    
  } catch (error) {
    console.log("❌ Error buscando ProxyAdmin:", error.message);
  }

  // Estrategia 2: Buscar en transactions históricas
  console.log("\n🔎 Alternative: Verificar si el deployer es el admin");
  
  // Para Transparent Proxy, a veces el deployer es el admin directamente
  const registry = await ethers.getContractAt("GanadoRegistryUpgradeable", registryAddress);
  
  try {
    // Intentar llamar una función que requiera upgrade
    const upgradeData = registry.interface.encodeFunctionData("upgradeTo", ["0x0000000000000000000000000000000000000000"]);
    console.log(`📋 Upgrade data: ${upgradeData}`);
    console.log("💡 Si puedes llamar upgradeTo, eres el admin");
  } catch (error) {
    console.log("❌ No tienes permisos de upgrade:", error.message);
  }
}

main().catch(console.error);