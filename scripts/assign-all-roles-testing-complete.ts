const { ethers } = require("hardhat");
const deployedAddresses = require("../deployed_addresses.json");

async function main() {
  console.log("==============================================");
  console.log("🚀 ASIGNANDO TODOS LOS ROLES (CONTRATO TESTING)");
  console.log("==============================================");

  const [deployer] = await ethers.getSigners();
  console.log(`🔑 Deployer: ${deployer.address}`);

  // Conectar al NUEVO contrato de testing (donde somos admin)
  const TokenFactory = await ethers.getContractFactory("GanadoTokenUpgradeable");
  const NFTFactory = await ethers.getContractFactory("AnimalNFTUpgradeable");
  const RegistryFactory = await ethers.getContractFactory("GanadoRegistryUpgradeable");

  // Usar el NUEVO contrato de testing para Token
  const token = TokenFactory.attach("0x4aEba083F69eDa5eE40924b66125aD79702f2170");
  // Usar contratos originales para NFT y Registry
  const nft = NFTFactory.attach(deployedAddresses.contracts.AnimalNFTUpgradeable);
  const registry = RegistryFactory.attach(deployedAddresses.contracts.GanadoRegistryUpgradeable);

  console.log("✅ Contratos conectados:");
  console.log(`   Token Testing: 0x4aEba083F69eDa5eE40924b66125aD79702f2170`);
  console.log(`   NFT Original: ${deployedAddresses.contracts.AnimalNFTUpgradeable}`);
  console.log(`   Registry Original: ${deployedAddresses.contracts.GanadoRegistryUpgradeable}`);

  // Obtener el rol de ADMIN por defecto
  const DEFAULT_ADMIN_ROLE = await token.DEFAULT_ADMIN_ROLE();

  console.log("\n👑 VERIFICANDO PERMISOS...");

  try {
    // Verificar que somos admin en el contrato de testing
    const isAdminToken = await token.hasRole(DEFAULT_ADMIN_ROLE, deployer.address);
    console.log(`   Admin en Token Testing: ${isAdminToken}`);

    // Intentar hacer deployer admin en NFT (puede fallar)
    try {
      const tx2 = await nft.grantRole(DEFAULT_ADMIN_ROLE, deployer.address);
      await tx2.wait();
      console.log("✅ Admin role otorgado en NFT");
    } catch (error) {
      console.log("⚠️  No se pudo otorgar admin en NFT (necesita Safe)");
    }

    // Intentar hacer deployer admin en Registry (puede fallar)
    try {
      const tx3 = await registry.grantRole(DEFAULT_ADMIN_ROLE, deployer.address);
      await tx3.wait();
      console.log("✅ Admin role otorgado en Registry");
    } catch (error) {
      console.log("⚠️  No se pudo otorgar admin en Registry (necesita Safe)");
    }

    console.log("\n🎯 ASIGNANDO ROLES EN TOKEN TESTING...");

    // Asignar todos los roles específicos al deployer EN EL CONTRATO DE TESTING
    const rolesToAssign = [
      // Token roles
      { contract: token, role: await token.DAO_ROLE(), name: "DAO_ROLE" },
      { contract: token, role: await token.MINTER_ROLE(), name: "MINTER_ROLE" },
      { contract: token, role: await token.PAUSER_ROLE(), name: "PAUSER_ROLE" },
      { contract: token, role: await token.UPGRADER_ROLE(), name: "UPGRADER_ROLE" },

      // NFT roles (intentar, pueden fallar)
      { contract: nft, role: await nft.PRODUCER_ROLE(), name: "PRODUCER_ROLE" },
      { contract: nft, role: await nft.VET_ROLE(), name: "VET_ROLE" },
      { contract: nft, role: await nft.FRIGORIFICO_ROLE(), name: "FRIGORIFICO_ROLE" },
      { contract: nft, role: await nft.AUDITOR_ROLE(), name: "AUDITOR_ROLE" },
      { contract: nft, role: await nft.PAUSER_ROLE(), name: "PAUSER_ROLE" },
      { contract: nft, role: await nft.UPGRADER_ROLE(), name: "UPGRADER_ROLE" },

      // Registry roles (intentar, pueden fallar)
      { contract: registry, role: await registry.DAO_ROLE(), name: "DAO_ROLE" },
      { contract: registry, role: await registry.UPGRADER_ROLE(), name: "UPGRADER_ROLE" },
      { contract: registry, role: await registry.PRODUCER_ROLE(), name: "PRODUCER_ROLE" },
      { contract: registry, role: await registry.VET_ROLE(), name: "VET_ROLE" },
      { contract: registry, role: await registry.FRIGORIFICO_ROLE(), name: "FRIGORIFICO_ROLE" },
      { contract: registry, role: await registry.AUDITOR_ROLE(), name: "AUDITOR_ROLE" },
      { contract: registry, role: await registry.IOT_ROLE(), name: "IOT_ROLE" }
    ];

    for (const { contract, role, name } of rolesToAssign) {
      try {
        const hasRoleAlready = await contract.hasRole(role, deployer.address);
        if (!hasRoleAlready) {
          const tx = await contract.grantRole(role, deployer.address);
          await tx.wait();
          console.log(`✅ ${name} otorgado`);
        } else {
          console.log(`⚠️  ${name} ya asignado`);
        }
      } catch (error) {
        console.log(`❌ ${name} no se pudo asignar: ${error.message}`);
      }
    }

    console.log("\n==============================================");
    console.log("🎉 ¡PROCESO COMPLETADO!");
    console.log("==============================================");
    console.log("📍 Token Testing: Todos los roles asignados");
    console.log("📍 NFT/Registry: Algunos roles pueden requerir Safe");
    console.log("==============================================");

  } catch (error) {
    console.error("❌ Error general:", error.message);
  }
}

main().catch(console.error);