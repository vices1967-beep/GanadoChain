// src/router/routes/index.ts
import { coreRoutes } from './core';
import { governanceRoutes } from './governance';
import { reportsRoutes } from './reports';
import { rewardsRoutes } from './rewards';
import { cattleRoutes } from './cattle'; // ← Añadir esta importación
// importar otras rutas

export const allRoutes = [
  ...coreRoutes,
  ...governanceRoutes,
  ...reportsRoutes,
  ...rewardsRoutes,
  ...cattleRoutes, // ← Añadir cattle routes
  // ... otras rutas
];
