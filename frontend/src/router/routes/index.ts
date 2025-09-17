import { coreRoutes } from './core';
import { governanceRoutes } from './governance';
import { reportsRoutes } from './reports';
import { rewardsRoutes } from './rewards';
// importar otras rutas

export const allRoutes = [
  ...coreRoutes,
  ...governanceRoutes,
  ...reportsRoutes,
  ...rewardsRoutes,
  // ... otras rutas
];
