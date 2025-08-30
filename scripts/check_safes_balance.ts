import { ethers } from "hardhat";
import fs from "fs";

async function main() {
  // Leer el archivo deployed_addresses.json
  const data = fs.readFileSync("deployed_addresses.json", "utf8");
  const deployed = JSON.parse(data);

  if (!deployed.safes) {
    console.error("⚠️ No se encontraron direcciones de safes en deployed_addresses.json");
    process.exit(1);
  }

  console.log("🔎 Consultando balances de las Safes en Amoy...\n");

  for (const [name, address] of Object.entries(deployed.safes)) {
    const balance = await ethers.provider.getBalance(address as string);
    console.log(
  `${name} (${address}) → ${ethers.formatEther(balance)} POL`
);

  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
