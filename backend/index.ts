import express from "express";
import cors from "cors";
import bodyParser from "body-parser";
import animalRoutes from "./routes/animals";

const app = express();
app.use(cors());
app.use(bodyParser.json());

app.use("/api/animals", animalRoutes);

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => console.log(`Backend corriendo en http://localhost:${PORT}`));
