const { ethers } = require("hardhat");
const newAddresses = require("../deployed-new.json");

async function main() {
  console.log("==============================================");
  console.log("🚀 TESTEO COMPLETO DE NFT");
  console.log("==============================================");

  const [deployer] = await ethers.getSigners();
  console.log(`🔑 Deployer: ${deployer.address}`);

  const NFTFactory = await ethers.getContractFactory("AnimalNFTUpgradeable");
  const nft = NFTFactory.attach(newAddresses.contracts.AnimalNFTUpgradeable);

  console.log("✅ Conectado al NFT:", nft.address);

  // 1. INFORMACIÓN BÁSICA
  console.log("\n📖 INFORMACIÓN BÁSICA:");
  console.log(`   Name: ${await nft.name()}`);
  console.log(`   Symbol: ${await nft.symbol()}`);

  // 2. TEST MINT NFT
  console.log("\n🔄 TEST MINT NFT:");
  const txMint = await nft.mintAnimal(
    deployer.address,
    "ipfs://QmTestMetadata123",
    "ipfs://QmTestOperational456"
  );
  await txMint.wait();
  console.log(`   ✅ NFT Minted - TX: ${txMint.hash}`);

  // 3. VERIFICAR NFT
  const nftBalance = await nft.balanceOf(deployer.address);
  const tokenId = 1;
  console.log(`   NFTs owned: ${nftBalance}`);
  console.log(`   Token URI: ${await nft.tokenURI(tokenId)}`);
  console.log(`   Owner of token 1: ${await nft.ownerOf(tokenId)}`);

  // 4. TEST ACTUALIZAR METADATA
  console.log("\n🔄 TEST UPDATE METADATA:");
  const txUpdate = await nft.updateAnimalURI(tokenId, "ipfs://QmNewMetadata789");
  await txUpdate.wait();
  console.log("   ✅ NFT metadata updated");

  // 5. TEST ROLES
  console.log("\n👑 VERIFICACIÓN DE ROLES:");
  const roles = {
    PRODUCER: await nft.PRODUCER_ROLE(),
    VET: await nft.VET_ROLE(),
    AUDITOR: await nft.AUDITOR_ROLE()
  };

  for (const [roleName, roleHash] of Object.entries(roles)) {
    const hasRole = await nft.hasRole(roleHash, deployer.address);
    console.log(`   ${roleName}: ${hasRole ? "✅" : "❌"} ${hasRole}`);
  }

  console.log("\n==============================================");
  console.log("🎉 TESTEO DE NFT COMPLETADO EXITOSAMENTE!");
  console.log("==============================================");
}

main().catch(console.error);