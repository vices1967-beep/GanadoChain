const { ethers } = require("hardhat");
const deployedAddresses = require("../deployed_addresses.json");

async function main() {
  console.log("==============================================");
  console.log("🚀 HACIENDO DEPLOYER ADMIN TEMPORAL (TESTING)");
  console.log("==============================================");

  const [deployer] = await ethers.getSigners();
  console.log(`🔑 Deployer: ${deployer.address}`);

  // Conectar a todos los contratos
  const TokenFactory = await ethers.getContractFactory("GanadoTokenUpgradeable");
  const NFTFactory = await ethers.getContractFactory("AnimalNFTUpgradeable");
  const RegistryFactory = await ethers.getContractFactory("GanadoRegistryUpgradeable");

  const token = TokenFactory.attach(deployedAddresses.contracts.GanadoTokenUpgradeable);
  const nft = NFTFactory.attach(deployedAddresses.contracts.AnimalNFTUpgradeable);
  const registry = RegistryFactory.attach(deployedAddresses.contracts.GanadoRegistryUpgradeable);

  // Obtener el rol de ADMIN por defecto de cada contrato
  const DEFAULT_ADMIN_ROLE = await token.DEFAULT_ADMIN_ROLE();

  console.log("\n👑 OTORGANDO ROLES DE ADMIN...");

  try {
    // Hacer deployer admin en Token
    const tx1 = await token.grantRole(DEFAULT_ADMIN_ROLE, deployer.address);
    await tx1.wait();
    console.log("✅ Admin role otorgado en Token");

    // Hacer deployer admin en NFT
    const tx2 = await nft.grantRole(DEFAULT_ADMIN_ROLE, deployer.address);
    await tx2.wait();
    console.log("✅ Admin role otorgado en NFT");

    // Hacer deployer admin en Registry
    const tx3 = await registry.grantRole(DEFAULT_ADMIN_ROLE, deployer.address);
    await tx3.wait();
    console.log("✅ Admin role otorgado en Registry");

    console.log("\n🎯 AHORA ASIGNANDO TODOS LOS ROLES ESPECÍFICOS...");

    // Asignar todos los roles específicos al deployer
    const rolesToAssign = [
      // Token roles
      { contract: token, role: await token.DAO_ROLE(), name: "DAO_ROLE" },
      { contract: token, role: await token.MINTER_ROLE(), name: "MINTER_ROLE" },
      { contract: token, role: await token.PAUSER_ROLE(), name: "PAUSER_ROLE" },
      { contract: token, role: await token.UPGRADER_ROLE(), name: "UPGRADER_ROLE" },

      // NFT roles
      { contract: nft, role: await nft.PRODUCER_ROLE(), name: "PRODUCER_ROLE" },
      { contract: nft, role: await nft.VET_ROLE(), name: "VET_ROLE" },
      { contract: nft, role: await nft.FRIGORIFICO_ROLE(), name: "FRIGORIFICO_ROLE" },
      { contract: nft, role: await nft.AUDITOR_ROLE(), name: "AUDITOR_ROLE" },
      { contract: nft, role: await nft.PAUSER_ROLE(), name: "PAUSER_ROLE" },
      { contract: nft, role: await nft.UPGRADER_ROLE(), name: "UPGRADER_ROLE" },

      // Registry roles
      { contract: registry, role: await registry.DAO_ROLE(), name: "DAO_ROLE" },
      { contract: registry, role: await registry.UPGRADER_ROLE(), name: "UPGRADER_ROLE" },
      { contract: registry, role: await registry.PRODUCER_ROLE(), name: "PRODUCER_ROLE" },
      { contract: registry, role: await registry.VET_ROLE(), name: "VET_ROLE" },
      { contract: registry, role: await registry.FRIGORIFICO_ROLE(), name: "FRIGORIFICO_ROLE" },
      { contract: registry, role: await registry.AUDITOR_ROLE(), name: "AUDITOR_ROLE" },
      { contract: registry, role: await registry.IOT_ROLE(), name: "IOT_ROLE" } // ✅ Rol IoT
    ];

    for (const { contract, role, name } of rolesToAssign) {
      const tx = await contract.grantRole(role, deployer.address);
      await tx.wait();
      console.log(`✅ ${name} otorgado`);
    }

    console.log("\n==============================================");
    console.log("🎉 ¡DEPLOYER AHORA TIENE TODOS LOS ROLES!");
    console.log("==============================================");
    console.log("📍 Puedes ejecutar interact.ts nuevamente");
    console.log("📍 Recuerda: Esto es SOLO para testing");
    console.log("==============================================");

  } catch (error) {
    console.error("❌ Error:", error.message);
    console.log("⚠️  Puede que ya tengas algunos roles");
  }
}

main().catch(console.error);