const { ethers } = require("hardhat");
const deployedAddresses = require("../deployed_addresses.json");

async function main() {
  console.log("==============================================");
  console.log("🚀 INTERACTUANDO CON CONTRATOS GANADOCHAIN");
  console.log("==============================================");

  // Obtener el signer
  const [deployer] = await ethers.getSigners();
  console.log(`🔑 Conectado como: ${deployer.address}`);

  // Conectar a los contratos
  const TokenFactory = await ethers.getContractFactory("GanadoTokenUpgradeable");
  const NFTFactory = await ethers.getContractFactory("AnimalNFTUpgradeable");
  const RegistryFactory = await ethers.getContractFactory("GanadoRegistryUpgradeable");

  const token = TokenFactory.attach(deployedAddresses.contracts.GanadoTokenUpgradeable);
  const nft = NFTFactory.attach(deployedAddresses.contracts.AnimalNFTUpgradeable);
  const registry = RegistryFactory.attach(deployedAddresses.contracts.GanadoRegistryUpgradeable);

  console.log("✅ Contratos conectados correctamente");

  // 1. LEER INFORMACIÓN BÁSICA
  console.log("\n📖 INFORMACIÓN DE CONTRATOS:");
  
  const tokenName = await token.name();
  const tokenSymbol = await token.symbol();
  const totalSupply = await token.totalSupply();
  console.log(`   Token: ${tokenName} (${tokenSymbol}) - Supply: ${ethers.utils.formatEther(totalSupply)}`);

  const nftName = await nft.name();
  const nftSymbol = await nft.symbol();
  console.log(`   NFT: ${nftName} (${nftSymbol})`);

  // 2. VERIFICAR ROLES
  console.log("\n👑 VERIFICACIÓN DE ROLES:");
  
  const hasDAORole = await token.hasRole(await token.DAO_ROLE(), deployer.address);
  const hasProducerRole = await nft.hasRole(await nft.PRODUCER_ROLE(), deployer.address);
  
  console.log(`   Rol DAO: ${hasDAORole}`);
  console.log(`   Rol Productor: ${hasProducerRole}`);

  // 3. OPERACIONES CON TOKENS (si tiene rol DAO)
  if (hasDAORole) {
    console.log("\n💰 OPERACIONES CON TOKENS:");
    
    try {
      // Mint de tokens
      const amount = ethers.utils.parseEther("500");
      const txMint = await token.mintByDAO(deployer.address, amount, "test-batch-001");
      await txMint.wait();
      console.log(`   ✅ Tokens minteados: 500 GFT - TX: ${txMint.hash}`);
      
      // Ver nuevo balance
      const newBalance = await token.balanceOf(deployer.address);
      console.log(`   Nuevo balance: ${ethers.utils.formatEther(newBalance)} GFT`);
      
    } catch (error) {
      console.log("   ⚠️  Error en operación de tokens:", error.message);
    }
  }

  console.log("\n==============================================");
  console.log("🎉 INTERACCIÓN COMPLETADA EXITOSAMENTE");
  console.log("==============================================");
}

main().catch((error) => {
  console.error("❌ Error en interacción:", error);
  process.exit(1);
});