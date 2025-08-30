import { fileURLToPath } from "url";
import path from "path";
import fs from "fs";
import hardhat from "hardhat";
const { ethers, upgrades } = hardhat;

import { SafeFactory, EthersAdapter } from "@safe-global/protocol-kit";

// Simula __dirname en ESM
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const deployedFile = path.join(__dirname, "../deployed_addresses.json");

async function main() {
  // Detectar la red
  const net = await ethers.provider.getNetwork();
  const network = net.name || "unknown";
  console.log(`Network: ${network}`);

  if (!fs.existsSync(deployedFile)) throw new Error("No deployed_addresses.json found");
  const deployedData = JSON.parse(fs.readFileSync(deployedFile, "utf8"));

  // ---------- AnimalNFTUpgradeable ----------
  const AnimalNFT = await ethers.getContractFactory("AnimalNFTUpgradeable");
  let animalNFTAddress = deployedData.contracts?.AnimalNFTUpgradeable || "";
  let animalNFT: any;

  if (animalNFTAddress) {
    console.log("Upgrading AnimalNFTUpgradeable at", animalNFTAddress);
    animalNFT = await upgrades.upgradeProxy(animalNFTAddress, AnimalNFT);
    await animalNFT.deployed();
    animalNFTAddress = animalNFT.address || animalNFT.target || (animalNFT as any).proxy?.address;
    if (!animalNFTAddress) throw new Error("AnimalNFTUpgradeable address is undefined after upgrade");
    console.log("Upgraded AnimalNFTUpgradeable at", animalNFTAddress);
  } else {
    console.log("Deploying new AnimalNFTUpgradeable...");
    const adminAddr =
      deployedData.safes?.mainSafe ||
      deployedData.safes?.deployer1 ||
      (await ethers.getSigners())[0].address;

    animalNFT = await upgrades.deployProxy(AnimalNFT, [adminAddr], { kind: "uups" });
    await animalNFT.deployed();
    animalNFTAddress = animalNFT.address || animalNFT.target || (animalNFT as any).proxy?.address;
    if (!animalNFTAddress) throw new Error("AnimalNFTUpgradeable address is undefined after deploy");
    console.log("Deployed AnimalNFTUpgradeable at", animalNFTAddress);
  }

  // ---------- GanadoRegistryUpgradeable ----------
  const GanadoRegistry = await ethers.getContractFactory("GanadoRegistryUpgradeable");
  let registryAddress = deployedData.contracts?.GanadoRegistryUpgradeable || "";
  let registry: any;

  const tokenAddr = deployedData.contracts?.GanadoTokenUpgradeable;
  if (!tokenAddr) throw new Error("GanadoTokenUpgradeable not found in deployed_addresses.json");

  if (registryAddress) {
    console.log("Upgrading GanadoRegistryUpgradeable at", registryAddress);
    registry = await upgrades.upgradeProxy(registryAddress, GanadoRegistry);
    await registry.deployed();
    registryAddress = registry.address || registry.target || (registry as any).proxy?.address;
    if (!registryAddress) throw new Error("GanadoRegistryUpgradeable address is undefined after upgrade");
    console.log("Upgraded GanadoRegistryUpgradeable at", registryAddress);
  } else {
    console.log("Deploying new GanadoRegistryUpgradeable...");
    const daoAdmin =
      deployedData.safes?.mainSafe ||
      deployedData.safes?.deployer1 ||
      (await ethers.getSigners())[0].address;

    registry = await upgrades.deployProxy(
      GanadoRegistry,
      [daoAdmin, tokenAddr, animalNFTAddress],
      { kind: "uups" }
    );
    await registry.deployed();
    registryAddress = registry.address || registry.target || (registry as any).proxy?.address;
    if (!registryAddress) throw new Error("GanadoRegistryUpgradeable address is undefined after deploy");
    console.log("Deployed GanadoRegistryUpgradeable at", registryAddress);
  }

  // ---------- Crear Safe Multisig con protocol-kit ----------
  if (!deployedData.safes) deployedData.safes = {};
  if (!deployedData.safes.mainSafe) {
    console.log("Creating new Safe multisig...");
    const signers = await ethers.getSigners();
    const signer = signers[0];
    const ethAdapter = new EthersAdapter({ ethers, signer });
    const safeFactory = await SafeFactory.create({ ethAdapter });

    const owners = [
      deployedData.safes.deployer1,
      deployedData.safes.deployer2,
      deployedData.safes.deployer3
    ].filter(Boolean);

    if (owners.length < 1) throw new Error("No deployer owners found in deployed_addresses.json");

    const safeAccountConfig = { owners, threshold: Math.min(2, owners.length) };
    const safeSdk = await safeFactory.deploySafe({ safeAccountConfig });
    const safeAddress = await safeSdk.getAddress();
    console.log("Safe deployed at", safeAddress);
    deployedData.safes.mainSafe = safeAddress;
  } else {
    console.log("Safe multisig already exists at", deployedData.safes.mainSafe);
  }

  // ---------- Actualizar JSON ----------
  deployedData.contracts = deployedData.contracts || {};
  deployedData.contracts.AnimalNFTUpgradeable = animalNFTAddress;
  deployedData.contracts.GanadoRegistryUpgradeable = registryAddress;
  deployedData.network = network;

  fs.writeFileSync(deployedFile, JSON.stringify(deployedData, null, 2));
  console.log("Updated deployed_addresses.json");
}

// Ejecutar script
main()
  .then(() => process.exit(0))
  .catch((err) => {
    console.error("ERROR:", err);
    process.exit(1);
  });
