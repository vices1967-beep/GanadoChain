// scripts/check-animals.ts
import { ethers } from "hardhat";
import * as fs from "fs";
import * as path from "path";

async function main() {
  console.log("🔍 VERIFICANDO ANIMALES EN BLOCKCHAIN");
  
  const deployedPath = path.join(__dirname, "..", "deployed-new.json");
  const deployedData = JSON.parse(fs.readFileSync(deployedPath, "utf8"));
  const nftAddress = deployedData.contracts.AnimalNFTUpgradeable;

  const [deployer] = await ethers.getSigners();

  // ABI simplificada para NFT
  const nftABI = [
    "function ownerOf(uint256 tokenId) external view returns (address)",
    "function balanceOf(address owner) external view returns (uint256)",
    "function tokenOfOwnerByIndex(address owner, uint256 index) external view returns (uint256)",
    "function exists(uint256 tokenId) external view returns (bool)"
  ];
  
  const nftContract = new ethers.Contract(nftAddress, nftABI, deployer);

  // Verificar balance del deployer
  const balance = await nftContract.balanceOf(deployer.address);
  console.log(`📊 NFTs en posesión de ${deployer.address}: ${balance}`);

  // Listar todos los NFTs del deployer
  for (let i = 0; i < balance; i++) {
    try {
      const tokenId = await nftContract.tokenOfOwnerByIndex(deployer.address, i);
      console.log(`✅ NFT ${i}: Token ID ${tokenId}`);
    } catch (error) {
      console.log(`❌ Error obteniendo NFT ${i}: ${error.message}`);
    }
  }

  // Verificar animales específicos
  const animalTokenIds = [10, 11];
  console.log("\n🔍 VERIFICANDO ANIMALES ESPECÍFICOS:");
  
  for (const tokenId of animalTokenIds) {
    try {
      const exists = await nftContract.exists(tokenId);
      if (exists) {
        const owner = await nftContract.ownerOf(tokenId);
        console.log(`✅ Animal ${tokenId}: Existe, Owner: ${owner}`);
      } else {
        console.log(`❌ Animal ${tokenId}: No existe`);
      }
    } catch (error) {
      console.log(`❌ Error con animal ${tokenId}: ${error.message}`);
    }
  }
}

main().catch(console.error);