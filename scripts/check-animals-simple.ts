// scripts/check-animals-simple.ts
import { ethers } from "hardhat";
import * as fs from "fs";
import * as path from "path";

async function main() {
  console.log("🔍 VERIFICANDO ANIMALES EN BLOCKCHAIN (MÉTODO SIMPLE)");
  
  const deployedPath = path.join(__dirname, "..", "deployed-new.json");
  const deployedData = JSON.parse(fs.readFileSync(deployedPath, "utf8"));
  const nftAddress = deployedData.contracts.AnimalNFTUpgradeable;

  const [deployer] = await ethers.getSigners();

  // ABI mínima para ERC721 básico
  const nftABI = [
    "function ownerOf(uint256 tokenId) external view returns (address)",
    "function balanceOf(address owner) external view returns (uint256)"
  ];
  
  const nftContract = new ethers.Contract(nftAddress, nftABI, deployer);

  // Verificar balance del deployer
  const balance = await nftContract.balanceOf(deployer.address);
  console.log(`📊 NFTs en posesión de ${deployer.address}: ${balance}`);

  // Verificar animales específicos usando ownerOf (más confiable)
  const animalTokenIds = [10, 11];
  console.log("\n🔍 VERIFICANDO ANIMALES ESPECÍFICOS CON ownerOf:");
  
  for (const tokenId of animalTokenIds) {
    try {
      const owner = await nftContract.ownerOf(tokenId);
      console.log(`✅ Animal ${tokenId}: Existe, Owner: ${owner}`);
      
      // Verificar si el owner es el deployer
      if (owner.toLowerCase() === deployer.address.toLowerCase()) {
        console.log(`   🎯 Pertenece al deployer`);
      } else {
        console.log(`   ⚠️ NO pertenece al deployer`);
      }
    } catch (error) {
      console.log(`❌ Animal ${tokenId}: No existe o error - ${error.message}`);
    }
  }

  // Verificar algunos token IDs comunes por si los animales tienen otros IDs
  console.log("\n🔍 BUSCANDO ANIMALES CON OTROS IDs:");
  const commonTokenIds = [1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 13, 14, 15];
  
  for (const tokenId of commonTokenIds) {
    try {
      const owner = await nftContract.ownerOf(tokenId);
      console.log(`✅ Token ${tokenId}: Existe, Owner: ${owner}`);
    } catch (error) {
      // Silenciar errores de tokens que no existen
    }
  }
}

main().catch(console.error);