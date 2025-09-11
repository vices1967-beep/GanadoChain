const { ethers, upgrades } = require("hardhat");

async function main() {
  const registryAddress = "0xFC81a60f26Aa98Ac4882A5B2A2c8C64430F36979";
  const implAddress = await upgrades.erc1967.getImplementationAddress(registryAddress);
  console.log("Implementation address:", implAddress);
}
main();