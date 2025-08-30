import { Router } from "express";
import { getContracts } from "../contracts";
import { uploadJson } from "../utils/ipfs";

const router = Router();

// Crear nuevo animal
router.post("/", async (req, res) => {
  try {
    const { id, species, weight, location, vaccines } = req.body;
    const { AnimalNFT, deployer } = await getContracts();

    const ipfsHash = await uploadJson({ id, species, weight, location, vaccines });
    const tx = await AnimalNFT.connect(deployer).mintAnimal(deployer.address, id, ipfsHash);
    await tx.wait();

    res.json({ success: true, ipfsHash, txHash: tx.hash });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Error al crear animal" });
  }
});

// Leer todos los animales (IDs y hashes)
router.get("/", async (_req, res) => {
  try {
    const { AnimalNFT } = await getContracts();
    const total = (await AnimalNFT.totalSupply()).toNumber();
    const animals = [];
    for (let i = 0; i < total; i++) {
      const tokenId = await AnimalNFT.tokenByIndex(i);
      const owner = await AnimalNFT.ownerOf(tokenId);
      const uri = await AnimalNFT.tokenURI(tokenId);
      animals.push({ tokenId: tokenId.toString(), owner, uri });
    }
    res.json(animals);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Error al obtener animales" });
  }
});

// Leer un animal por ID
router.get("/:id", async (req, res) => {
  try {
    const { AnimalNFT } = await getContracts();
    const tokenId = req.params.id;
    const owner = await AnimalNFT.ownerOf(tokenId);
    const uri = await AnimalNFT.tokenURI(tokenId);
    res.json({ tokenId, owner, uri });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Error al obtener animal" });
  }
});

// Actualizar datos de un animal (solo IPFS, NFT sigue igual)
router.put("/:id", async (req, res) => {
  try {
    const { AnimalNFT, deployer } = await getContracts();
    const tokenId = req.params.id;
    const { species, weight, location, vaccines } = req.body;

    const ipfsHash = await uploadJson({ id: tokenId, species, weight, location, vaccines });
    const tx = await AnimalNFT.connect(deployer).updateAnimalURI(tokenId, ipfsHash); // Supone función en contrato
    await tx.wait();

    res.json({ success: true, ipfsHash, txHash: tx.hash });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Error al actualizar animal" });
  }
});

// Eliminar animal (quemar NFT)
router.delete("/:id", async (req, res) => {
  try {
    const { AnimalNFT, deployer } = await getContracts();
    const tokenId = req.params.id;
    const tx = await AnimalNFT.connect(deployer).burnAnimal(tokenId); // Supone función burn
    await tx.wait();
    res.json({ success: true, txHash: tx.hash });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Error al eliminar animal" });
  }
});

export default router;
