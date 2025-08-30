import { Router } from "express";
import { getContracts } from "../contracts";

const router = Router();

// Ejemplo: asignar animal a lote
router.post("/assign-animal", async (req, res) => {
  try {
    const { Registry, deployer } = await getContracts();
    const { batchId, animalId } = req.body;

    const tx = await Registry.connect(deployer).assignAnimalToBatch(animalId, batchId);
    await tx.wait();

    res.json({ success: true, txHash: tx.hash });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Error al asignar animal a lote" });
  }
});

export default router;
