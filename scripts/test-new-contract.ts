// scripts/test-new-contract.ts
const { ethers } = require("hardhat");

async function main() {
  console.log("==============================================");
  console.log("🚀 TESTEANDO NUEVO CONTRATO CON ADMIN");
  console.log("==============================================");

  const [deployer] = await ethers.getSigners();
  console.log(`🔑 Admin: ${deployer.address}`);

  const TokenFactory = await ethers.getContractFactory("GanadoTokenUpgradeable");
  const token = TokenFactory.attach("0x4aEba083F69eDa5eE40924b66125aD79702f2170");

  // ✅ AHORA SÍ PODRÁS HACER TODO:
  console.log("\n💰 MINTEANDO TOKENS...");
  const tx = await token.mintByDAO(deployer.address, ethers.utils.parseEther("1000"), "test-batch");
  await tx.wait();
  console.log("✅ 1000 tokens minteados!");

  // Ver balance
  const balance = await token.balanceOf(deployer.address);
  console.log(`📊 Balance: ${ethers.utils.formatEther(balance)} GFT`);

  console.log("\n🎉 ¡TODO FUNCIONANDO CORRECTAMENTE!");
}

main().catch(console.error);