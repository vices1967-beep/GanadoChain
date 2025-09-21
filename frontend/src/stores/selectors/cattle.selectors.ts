// frontend/src/stores/selectors/cattle.selectors.ts
import { createSelector } from '@reduxjs/toolkit';
import { RootState } from '../store';

export const selectCattleState = (state: RootState) => state.cattle;

export const selectAnimals = createSelector(
  selectCattleState,
  (cattle) => cattle.animals
);

export const selectAnimalById = createSelector(
  [selectAnimals, (_, animalId: number) => animalId],
  (animals, animalId) => animals.find(animal => animal.id === animalId)
);

export const selectBatches = createSelector(
  selectCattleState,
  (cattle) => cattle.batches
);

export const selectBatchById = createSelector(
  [selectBatches, (_, batchId: number) => batchId],
  (batches, batchId) => batches.find(batch => batch.id === batchId)
);

export const selectStats = createSelector(
  selectCattleState,
  (cattle) => cattle.stats
);

export const selectSelectedAnimal = createSelector(
  selectCattleState,
  (cattle) => cattle.selectedAnimal
);

export const selectSelectedBatch = createSelector(
  selectCattleState,
  (cattle) => cattle.selectedBatch
);

export const selectLoading = createSelector(
  selectCattleState,
  (cattle) => cattle.loading
);

export const selectError = createSelector(
  selectCattleState,
  (cattle) => cattle.error
);

export const selectAnimalsByStatus = createSelector(
  [selectAnimals, (_, status: string) => status],
  (animals, status) => animals.filter(animal => animal.status === status)
);

export const selectAnimalsByHealth = createSelector(
  [selectAnimals, (_, healthStatus: string) => healthStatus],
  (animals, healthStatus) => animals.filter(animal => animal.health_status === healthStatus)
);

// Añadir estos nuevos selectores
export const selectCertifications = createSelector(
  selectCattleState,
  (cattle) => cattle.certifications
);

export const selectCertificationStandards = createSelector(
  selectCattleState,
  (cattle) => cattle.certificationStandards || []
);