import { ethers } from "hardhat";
import Safe, { SafeFactory } from "@safe-global/safe-core-sdk";
import EthersAdapter from "@safe-global/safe-ethers-lib";
import fs from "fs";
import path from "path";

async function main() {
  // Ruta del archivo JSON con direcciones actuales
  const deployedPath = path.join(__dirname, "../deployed_addresses.json");
  const deployedRaw = fs.readFileSync(deployedPath, "utf8");
  const deployed = JSON.parse(deployedRaw);

  const [deployer] = await ethers.getSigners();
  const ethAdapter = new EthersAdapter({ ethers, signer: deployer });
  const safeFactory = await SafeFactory.create({ ethAdapter });

  // Tomamos los owners desde el JSON
  const owners = Object.values(deployed.safes);
  const threshold = 2; // Mínimo de firmas requeridas

  // Desplegar Safe
  const safeSdk: Safe = await safeFactory.deploySafe({ owners, threshold });
  const safeAddress = await safeSdk.getAddress();
  console.log("Safe Address creada:", safeAddress);

  // Guardar la nueva Safe en el JSON
  deployed.safes.realSafe = safeAddress;
  deployed.contracts.GanadoSafeMultisig = safeAddress;

  fs.writeFileSync(deployedPath, JSON.stringify(deployed, null, 2));
  console.log("Archivo deployed_addresses.json actualizado correctamente.");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
