import { ethers } from "hardhat";
import Safe, { SafeFactory } from "@safe-global/safe-core-sdk";
import EthersAdapter from "@safe-global/safe-ethers-lib";
import fs from "fs";
import path from "path";

const deployedPath = path.join(__dirname, "../deployed_addresses.json");
const deployed = JSON.parse(fs.readFileSync(deployedPath, "utf8"));

export async function getContracts() {
  const [deployer] = await ethers.getSigners();
  const GanadoToken = await ethers.getContractAt(
    "GanadoTokenUpgradeable",
    deployed.contracts.GanadoTokenUpgradeable
  );
  const AnimalNFT = await ethers.getContractAt(
    "AnimalNFTUpgradeable",
    deployed.contracts.AnimalNFTUpgradeable
  );
  const Registry = await ethers.getContractAt(
    "GanadoRegistryUpgradeable",
    deployed.contracts.GanadoRegistryUpgradeable
  );

  // Configurar Safe
  const ethAdapter = new EthersAdapter({ ethers, signer: deployer });
  const safeSdk: Safe = await Safe.create({ ethAdapter, safeAddress: deployed.safes.realSafe });

  return { GanadoToken, AnimalNFT, Registry, safeSdk, deployer };
}
