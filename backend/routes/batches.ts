import { Router } from "express";
import { getContracts } from "../contracts";
import { uploadJson } from "../utils/ipfs";

const router = Router();

// Crear lote
router.post("/", async (req, res) => {
  try {
    const { batchId, animalIds, description } = req.body;
    const { Registry, deployer } = await getContracts();

    const ipfsHash = await uploadJson({ batchId, animalIds, description });
    const tx = await Registry.connect(deployer).createBatch(batchId, animalIds, ipfsHash);
    await tx.wait();

    res.json({ success: true, ipfsHash, txHash: tx.hash });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Error al crear lote" });
  }
});

// Leer todos los lotes
router.get("/", async (_req, res) => {
  try {
    const { Registry } = await getContracts();
    const total = (await Registry.totalBatches()).toNumber();
    const batches = [];
    for (let i = 0; i < total; i++) {
      const batchId = await Registry.batchByIndex(i);
      const batchData = await Registry.getBatch(batchId);
      batches.push(batchData);
    }
    res.json(batches);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Error al obtener lotes" });
  }
});

// Leer lote por ID
router.get("/:id", async (req, res) => {
  try {
    const { Registry } = await getContracts();
    const batchId = req.params.id;
    const batchData = await Registry.getBatch(batchId);
    res.json(batchData);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Error al obtener lote" });
  }
});

// Actualizar lote (solo IPFS)
router.put("/:id", async (req, res) => {
  try {
    const { Registry, deployer } = await getContracts();
    const batchId = req.params.id;
    const { animalIds, description } = req.body;

    const ipfsHash = await uploadJson({ batchId, animalIds, description });
    const tx = await Registry.connect(deployer).updateBatch(batchId, ipfsHash);
    await tx.wait();

    res.json({ success: true, ipfsHash, txHash: tx.hash });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Error al actualizar lote" });
  }
});

// Eliminar lote
router.delete("/:id", async (req, res) => {
  try {
    const { Registry, deployer } = await getContracts();
    const batchId = req.params.id;
    const tx = await Registry.connect(deployer).deleteBatch(batchId);
    await tx.wait();
    res.json({ success: true, txHash: tx.hash });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Error al eliminar lote" });
  }
});

export default router;
