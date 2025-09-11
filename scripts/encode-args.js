const { ethers } = require("hardhat");

async function main() {
  const daoAdmin = "0xf27c409539ac5a5deb6fe0fcac5434ad9867b310";
  const tokenAddr = "0x0000000000000000000000000000000000000000";
  const nftAddr = "0x0000000000000000000000000000000000000000";
  
  const abiCoder = new ethers.utils.AbiCoder();
  const encodedArgs = abiCoder.encode(
    ["address", "address", "address"],
    [daoAdmin, tokenAddr, nftAddr]
  );
  
  console.log("Encoded constructor arguments:", encodedArgs);
  console.log("Without 0x prefix:", encodedArgs.slice(2));
}

main();