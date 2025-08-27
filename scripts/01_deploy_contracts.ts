import { ethers, upgrades } from "hardhat";
import 'dotenv/config';

const SAFE_ADDRESS = process.env.SAFE_ADDRESS as string;

async function main() {
  if (!SAFE_ADDRESS) {
    throw new Error("❌ Debes definir SAFE_ADDRESS en tu .env");
  }

  const [deployer] = await ethers.getSigners();
  console.log("Deployer temporal:", deployer.address);

  // 1) Deploy GanadoToken (upgradeable)
  const GanadoToken = await ethers.getContractFactory("GanadoTokenUpgradeable");
  const initialCap = ethers.parseUnits("10000000", 18); // Cap 10M
  const token = await upgrades.deployProxy(
    GanadoToken,
    [deployer.address, 0, initialCap],
    { kind: "uups" }
  );
  await token.deployed();
  console.log("✅ GanadoToken (proxy) desplegado en:", token.target ?? token.address);

  // 2) Deploy AnimalNFT (upgradeable)
  const AnimalNFT = await ethers.getContractFactory("AnimalNFTUpgradeable");
  const nft = await upgrades.deployProxy(AnimalNFT, [deployer.address], { kind: "uups" });
  await nft.deployed();
  console.log("✅ AnimalNFT (proxy) desplegado en:", nft.target ?? nft.address);

  // 3) Deploy GanadoRegistry (upgradeable)
  const GanadoRegistry = await ethers.getContractFactory("GanadoRegistryUpgradeable");
  const registry = await upgrades.deployProxy(
    GanadoRegistry,
    [deployer.address, token.target ?? token.address, nft.target ?? nft.address],
    { kind: "uups" }
  );
  await registry.deployed();
  console.log("✅ GanadoRegistry (proxy) desplegado en:", registry.target ?? registry.address);

  // 4) Roles
  const MINTER_ROLE = await token.MINTER_ROLE();
  const DAO_ROLE = await token.DAO_ROLE();
  const UPGRADER_ROLE = await token.UPGRADER_ROLE();

  // 4a) Asignar MINTER_ROLE temporal al deployer (para pruebas)
  await (await token.grantRole(MINTER_ROLE, deployer.address)).wait();
  console.log("⚠ MINTER_ROLE otorgado al deployer temporalmente");

  // 4b) Asignar DAO_ROLE y UPGRADER_ROLE al Safe multisig
  await (await token.grantRole(DAO_ROLE, SAFE_ADDRESS)).wait();
  await (await token.grantRole(UPGRADER_ROLE, SAFE_ADDRESS)).wait();
  console.log(`✅ DAO_ROLE y UPGRADER_ROLE otorgados al Safe multisig: ${SAFE_ADDRESS}`);

  // 4c) Revocar MINTER_ROLE al deployer
  await (await token.revokeRole(MINTER_ROLE, deployer.address)).wait();
  console.log(`✅ MINTER_ROLE revocado del deployer temporal. Safe ahora controla todos los roles críticos.`);

  console.log("🎉 Deploy completo y seguro para producción.");
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
