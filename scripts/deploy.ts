import fs from "fs";
import { ethers, upgrades } from "hardhat";
import { encode as rlpEncode } from "@ethersproject/rlp";

interface DeployedAddresses {
  network: string;
  safes: { [key: string]: string };
  contracts: { [key: string]: string };
}

// Función corregida para calcular direcciones de contratos
function computeAddress(deployer: string, nonce: number): string {
  const nonceBytes = nonce === 0 ? new Uint8Array([]) : ethers.toBeArray(nonce);
  const rlpEncoded = rlpEncode([deployer, nonceBytes]);
  const hash = ethers.keccak256(rlpEncoded);
  return "0x" + hash.slice(-40);
}

async function main() {
  console.log("==============================================");
  console.log("🚀 GANADOCHAIN DEPLOY COMPLETO CON MULTISIG Y JSON");
  console.log("==============================================");

  const RPC_URL = process.env.RPC_URL!;
  const PRIVATE_KEYS = [
    process.env.PRIVATE_KEY!,
    process.env.PRIVATE_KEY_2!,
    process.env.PRIVATE_KEY_3!,
  ];

  if (!RPC_URL || PRIVATE_KEYS.some(k => !k)) {
    throw new Error("⚠️ Faltan PRIVATE_KEY o RPC_URL en .env");
  }

  const provider = new ethers.JsonRpcProvider(RPC_URL);
  const deployers = PRIVATE_KEYS.map(k => new ethers.Wallet(k, provider));

  // Mostrar saldos
  for (let i = 0; i < deployers.length; i++) {
    const balance = await provider.getBalance(deployers[i].address);
    console.log(`Deployer ${i + 1}: ${deployers[i].address} | Saldo: ${ethers.formatEther(balance)} MATIC`);
    if (balance < ethers.parseEther("0.01")) {
      throw new Error(`❌ Saldo insuficiente para deployer ${i + 1}`);
    }
  }

  // Calcular direcciones futuras de los safes
  const safes: { [key: string]: string } = {};
  for (let i = 0; i < deployers.length; i++) {
    const nonce = await provider.getTransactionCount(deployers[i].address);
    safes[`deployer${i + 1}`] = computeAddress(deployers[i].address, nonce);
    console.log(`Safe futura deployer ${i + 1}: ${safes[`deployer${i + 1}`]}`);
  }

  const deployed: DeployedAddresses = {
    network: "polygon-amoy",
    safes,
    contracts: {
      GanadoTokenUpgradeable: "",
      AnimalNFTUpgradeable: "",
      GanadoRegistryUpgradeable: "",
    },
  };

  const daoAdmin = safes.deployer1;
  const initialSupply = ethers.parseEther("1000000");
  const cap = ethers.parseEther("10000000");

  try {
    // ---------------------------
    // GanadoTokenUpgradeable
    // ---------------------------
    console.log("\n🔨 Desplegando GanadoTokenUpgradeable...");
    const TokenFactory = await ethers.getContractFactory("GanadoTokenUpgradeable", deployers[0]);
    const token = await upgrades.deployProxy(TokenFactory, [daoAdmin, initialSupply, cap], { kind: "uups" });
    await token.waitForDeployment();
    deployed.contracts.GanadoTokenUpgradeable = await token.getAddress();
    console.log("✅ GanadoTokenUpgradeable desplegado en:", deployed.contracts.GanadoTokenUpgradeable);

    // ---------------------------
    // AnimalNFTUpgradeable
    // ---------------------------
    console.log("\n🔨 Desplegando AnimalNFTUpgradeable...");
    const NFTFactory = await ethers.getContractFactory("AnimalNFTUpgradeable", deployers[0]);
    const nft = await upgrades.deployProxy(NFTFactory, [daoAdmin], { kind: "uups" });
    await nft.waitForDeployment();
    deployed.contracts.AnimalNFTUpgradeable = await nft.getAddress();
    console.log("✅ AnimalNFTUpgradeable desplegado en:", deployed.contracts.AnimalNFTUpgradeable);

    // ---------------------------
    // GanadoRegistryUpgradeable
    // ---------------------------
    console.log("\n🔨 Desplegando GanadoRegistryUpgradeable...");
    const RegistryFactory = await ethers.getContractFactory("GanadoRegistryUpgradeable", deployers[0]);
    const registry = await upgrades.deployProxy(
      RegistryFactory,
      [daoAdmin, deployed.contracts.GanadoTokenUpgradeable, deployed.contracts.AnimalNFTUpgradeable],
      { kind: "uups" }
    );
    await registry.waitForDeployment();
    deployed.contracts.GanadoRegistryUpgradeable = await registry.getAddress();
    console.log("✅ GanadoRegistryUpgradeable desplegado en:", deployed.contracts.GanadoRegistryUpgradeable);

    // Guardar JSON final
    fs.writeFileSync("deployed_addresses.json", JSON.stringify(deployed, null, 2));
    console.log("\n🎉 Deploy completado y direcciones guardadas en deployed_addresses.json");
    console.log("==============================================");

  } catch (err) {
    console.error("❌ Error durante deploy:", err);
    process.exit(1);
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Error en script:", error);
    process.exit(1);
  });