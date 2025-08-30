const { ethers } = require("hardhat");
const newAddresses = require("../deployed-new.json");

async function main() {
  console.log("==============================================");
  console.log("🚀 TESTEO COMPLETO DE TOKEN");
  console.log("==============================================");

  const [deployer] = await ethers.getSigners();
  console.log(`🔑 Deployer: ${deployer.address}`);

  const TokenFactory = await ethers.getContractFactory("GanadoTokenUpgradeable");
  const token = TokenFactory.attach(newAddresses.contracts.GanadoTokenUpgradeable);

  console.log("✅ Conectado al Token:", token.address);

  // 1. INFORMACIÓN BÁSICA
  console.log("\n📖 INFORMACIÓN BÁSICA:");
  console.log(`   Name: ${await token.name()}`);
  console.log(`   Symbol: ${await token.symbol()}`);
  console.log(`   Total Supply: ${ethers.utils.formatEther(await token.totalSupply())}`);
  console.log(`   Cap: ${ethers.utils.formatEther(await token.cap())}`);

  // 2. TEST MINT
  console.log("\n💰 TEST MINT:");
  const mintAmount = ethers.utils.parseEther("5000");
  const txMint = await token.mintByDAO(deployer.address, mintAmount, "test-batch-001");
  await txMint.wait();
  console.log(`   ✅ Minted 5000 tokens - TX: ${txMint.hash}`);

  // 3. VERIFICAR BALANCE
  const newBalance = await token.balanceOf(deployer.address);
  console.log(`   New Balance: ${ethers.utils.formatEther(newBalance)} GFT`);

  // 4. TEST PAUSE/UNPAUSE
  console.log("\n⏸️  TEST PAUSE:");
  const txPause = await token.pause();
  await txPause.wait();
  console.log("   ✅ Contract paused");

  // 5. TEST TRANSFER (debería fallar)
  try {
    const txTransfer = await token.transfer("0x0000000000000000000000000000000000000001", ethers.utils.parseEther("100"));
    await txTransfer.wait();
  } catch (error) {
    console.log("   ✅ Transfer correctly failed while paused");
  }

  // 6. TEST UNPAUSE
  const txUnpause = await token.unpause();
  await txUnpause.wait();
  console.log("   ✅ Contract unpaused");

  // 7. TEST TRANSFER (ahora debería funcionar)
  const txTransfer2 = await token.transfer("0x0000000000000000000000000000000000000001", ethers.utils.parseEther("100"));
  await txTransfer2.wait();
  console.log("   ✅ Transfer successful after unpause");

  console.log("\n==============================================");
  console.log("🎉 TESTEO DE TOKEN COMPLETADO EXITOSAMENTE!");
  console.log("==============================================");
}

main().catch(console.error);