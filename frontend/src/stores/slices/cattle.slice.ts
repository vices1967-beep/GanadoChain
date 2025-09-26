// src/stores/slices/cattle.slice.ts
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { cattleService } from '../../services/cattle/cattleService';
import { Animal, Batch, AnimalCertification, CattleStats, CertificationStandard } from '../../types/domain/cattle';

interface CattleState {
  animals: Animal[];
  batches: Batch[];
  certifications: AnimalCertification[];
  certificationStandards: CertificationStandard[];
  stats: CattleStats | null;
  selectedAnimal: Animal | null;
  selectedBatch: Batch | null;
  loading: boolean;
  error: string | null;
}

const initialState: CattleState = {
  animals: [],
  batches: [],
  certifications: [],
  certificationStandards: [],
  stats: null,
  selectedAnimal: null,
  selectedBatch: null,
  loading: false,
  error: null
};

// Async thunks
export const fetchAnimals = createAsyncThunk(
  'cattle/fetchAnimals',
  async (params?: any) => {
    const response = await cattleService.getAnimals(params);
    return response.data;
  }
);

export const fetchAnimal = createAsyncThunk(
  'cattle/fetchAnimal',
  async (id: number) => {
    return await cattleService.getAnimal(id);
  }
);

export const createAnimal = createAsyncThunk(
  'cattle/createAnimal',
  async (animalData: any) => {
    return await cattleService.createAnimal(animalData);
  }
);

export const updateAnimal = createAsyncThunk(
  'cattle/updateAnimal',
  async ({ id, animalData }: { id: number; animalData: any }) => {
    return await cattleService.updateAnimal(id, animalData);
  }
);

export const deleteAnimal = createAsyncThunk(
  'cattle/deleteAnimal',
  async (id: number) => {
    await cattleService.deleteAnimal(id);
    return id;
  }
);

export const fetchBatches = createAsyncThunk(
  'cattle/fetchBatches',
  async (params?: any) => {
    return await cattleService.getBatches(params);
  }
);

export const fetchBatch = createAsyncThunk(
  'cattle/fetchBatch',
  async (id: number) => {
    return await cattleService.getBatch(id);
  }
);

export const createBatch = createAsyncThunk(
  'cattle/createBatch',
  async (batchData: any) => {
    return await cattleService.createBatch(batchData);
  }
);

export const fetchStats = createAsyncThunk(
  'cattle/fetchStats',
  async () => {
    return await cattleService.getCattleStats();
  }
);

// Nuevos thunks para las funcionalidades faltantes
export const fetchCertificationStandards = createAsyncThunk(
  'cattle/fetchCertificationStandards',
  async () => {
    return await cattleService.getCertificationStandards();
  }
);

export const fetchAnimalCertifications = createAsyncThunk(
  'cattle/fetchAnimalCertifications',
  async (animalId: number) => {
    return await cattleService.getAnimalCertifications(animalId);
  }
);

export const revokeCertification = createAsyncThunk(
  'cattle/revokeCertification',
  async ({ certificationId, reason }: { certificationId: number; reason: string }) => {
    const response = await cattleService.revokeCertification(certificationId, reason);
    return { certificationId, reason, response };
  }
);

export const fetchAnimalHealthRecords = createAsyncThunk(
  'cattle/fetchAnimalHealthRecords',
  async (animalId: number) => {
    return await cattleService.getAnimalHealthRecords(animalId);
  }
);

export const mintAnimalNFT = createAsyncThunk(
  'cattle/mintAnimalNFT',
  async ({ animalId, mintData }: { animalId: number; mintData: any }) => {
    return await cattleService.mintAnimalNFT(animalId, mintData);
  }
);

export const transferAnimal = createAsyncThunk(
  'cattle/transferAnimal',
  async ({ animalId, transferData }: { animalId: number; transferData: any }) => {
    return await cattleService.transferAnimal(animalId, transferData);
  }
);

export const updateAnimalHealth = createAsyncThunk(
  'cattle/updateAnimalHealth',
  async ({ animalId, healthData }: { animalId: number; healthData: any }) => {
    return await cattleService.updateAnimalHealth(animalId, healthData);
  }
);

export const verifyAnimalNFT = createAsyncThunk(
  'cattle/verifyAnimalNFT',
  async (animalId: number) => {
    return await cattleService.verifyAnimalNFT(animalId);
  }
);

export const getAnimalNFTInfo = createAsyncThunk(
  'cattle/getAnimalNFTInfo',
  async (animalId: number) => {
    return await cattleService.getAnimalNFTInfo(animalId);
  }
);

export const getAnimalBlockchainEvents = createAsyncThunk(
  'cattle/getAnimalBlockchainEvents',
  async (animalId: number) => {
    return await cattleService.getAnimalBlockchainEvents(animalId);
  }
);

export const getAnimalAuditTrail = createAsyncThunk(
  'cattle/getAnimalAuditTrail',
  async (animalId: number) => {
    return await cattleService.getAnimalAuditTrail(animalId);
  }
);

export const updateBatchStatus = createAsyncThunk(
  'cattle/updateBatchStatus',
  async ({ batchId, statusData }: { batchId: number; statusData: any }) => {
    return await cattleService.updateBatchStatus(batchId, statusData);
  }
);

export const addAnimalsToBatch = createAsyncThunk(
  'cattle/addAnimalsToBatch',
  async ({ batchId, animalsData }: { batchId: number; animalsData: any }) => {
    return await cattleService.addAnimalsToBatch(batchId, animalsData);
  }
);

export const removeAnimalsFromBatch = createAsyncThunk(
  'cattle/removeAnimalsFromBatch',
  async ({ batchId, animalsData }: { batchId: number; animalsData: any }) => {
    return await cattleService.removeAnimalsFromBatch(batchId, animalsData);
  }
);

export const getBatchBlockchainEvents = createAsyncThunk(
  'cattle/getBatchBlockchainEvents',
  async (batchId: number) => {
    return await cattleService.getBatchBlockchainEvents(batchId);
  }
);

export const getBatchAuditTrail = createAsyncThunk(
  'cattle/getBatchAuditTrail',
  async (batchId: number) => {
    return await cattleService.getBatchAuditTrail(batchId);
  }
);

export const searchBatches = createAsyncThunk(
  'cattle/searchBatches',
  async (params: any) => {
    const response = await cattleService.searchBatches(params);
    return response.results;
  }
);

export const searchAnimals = createAsyncThunk(
  'cattle/searchAnimals',
  async (params: any) => {
    const response = await cattleService.searchAnimals(params);
    return response.results;
  }
);

export const exportAuditTrail = createAsyncThunk(
  'cattle/exportAuditTrail',
  async ({ format, days }: { format?: 'json' | 'csv'; days?: number }) => {
    return await cattleService.exportAuditTrail(format, days);
  }
);

const cattleSlice = createSlice({
  name: 'cattle',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    clearSelection: (state) => {
      state.selectedAnimal = null;
      state.selectedBatch = null;
    },
    selectAnimal: (state, action: PayloadAction<Animal | null>) => {
      state.selectedAnimal = action.payload;
    },
    selectBatch: (state, action: PayloadAction<Batch | null>) => {
      state.selectedBatch = action.payload;
    }
  },
  extraReducers: (builder) => {
    builder
      // Animals
      .addCase(fetchAnimals.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAnimals.fulfilled, (state, action) => {
        state.loading = false;
        state.animals = action.payload;
      })
      .addCase(fetchAnimals.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch animals';
      })
      .addCase(fetchAnimal.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAnimal.fulfilled, (state, action) => {
        state.loading = false;
        state.selectedAnimal = action.payload;
      })
      .addCase(fetchAnimal.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch animal';
      })
      .addCase(createAnimal.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createAnimal.fulfilled, (state, action) => {
        state.loading = false;
        state.animals.push(action.payload);
      })
      .addCase(createAnimal.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to create animal';
      })
      .addCase(updateAnimal.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.animals.findIndex(animal => animal.id === action.payload.id);
        if (index !== -1) {
          state.animals[index] = action.payload;
        }
        if (state.selectedAnimal?.id === action.payload.id) {
          state.selectedAnimal = action.payload;
        }
      })
      .addCase(deleteAnimal.fulfilled, (state, action) => {
        state.loading = false;
        state.animals = state.animals.filter(animal => animal.id !== action.payload);
        if (state.selectedAnimal?.id === action.payload) {
          state.selectedAnimal = null;
        }
      })
      // Batches
      .addCase(fetchBatches.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchBatches.fulfilled, (state, action) => {
        state.loading = false;
        state.batches = action.payload;
      })
      .addCase(fetchBatches.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch batches';
      })
      .addCase(fetchBatch.fulfilled, (state, action) => {
        state.loading = false;
        state.selectedBatch = action.payload;
      })
      .addCase(createBatch.fulfilled, (state, action) => {
        state.loading = false;
        state.batches.push(action.payload);
      })
      // Stats
      .addCase(fetchStats.fulfilled, (state, action) => {
        state.loading = false;
        state.stats = action.payload;
      })
      // Certifications
      .addCase(fetchCertificationStandards.fulfilled, (state, action) => {
        state.loading = false;
        state.certificationStandards = action.payload;
      })
      .addCase(fetchAnimalCertifications.fulfilled, (state, action) => {
        state.loading = false;
        state.certifications = action.payload;
      })
      .addCase(revokeCertification.fulfilled, (state, action) => {
        state.loading = false;
        // Actualizar el estado de la certificación revocada
        const index = state.certifications.findIndex(cert => cert.id === action.payload.certificationId);
        if (index !== -1) {
          state.certifications[index] = {
            ...state.certifications[index],
            status: 'REVOKED',
            revoked: true,
            revocation_reason: action.payload.reason // CORREGIDO: usar reason del payload
          };
        }
      })
      // Health Records
      .addCase(fetchAnimalHealthRecords.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAnimalHealthRecords.fulfilled, (state) => {
        state.loading = false;
        // Los health records no se almacenan en el estado global, se manejan en componentes
      })
      .addCase(fetchAnimalHealthRecords.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch health records';
      })
      // Para las demás acciones, solo manejar loading/error
      .addCase(mintAnimalNFT.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(mintAnimalNFT.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to mint NFT';
      })
      .addCase(transferAnimal.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(transferAnimal.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to transfer animal';
      })
      .addCase(updateAnimalHealth.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateAnimalHealth.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to update health';
      })
      // Para las acciones que solo consultan datos (no modifican el estado global)
      .addCase(verifyAnimalNFT.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(verifyAnimalNFT.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to verify NFT';
      })
      .addCase(getAnimalNFTInfo.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getAnimalNFTInfo.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to get NFT info';
      })
      .addCase(getAnimalBlockchainEvents.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getAnimalBlockchainEvents.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to get blockchain events';
      })
      .addCase(getAnimalAuditTrail.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getAnimalAuditTrail.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to get audit trail';
      })
      // Batch operations
      .addCase(updateBatchStatus.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateBatchStatus.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to update batch status';
      })
      .addCase(addAnimalsToBatch.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(addAnimalsToBatch.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to add animals to batch';
      })
      .addCase(removeAnimalsFromBatch.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(removeAnimalsFromBatch.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to remove animals from batch';
      })
      .addCase(getBatchBlockchainEvents.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getBatchBlockchainEvents.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to get batch blockchain events';
      })
      .addCase(getBatchAuditTrail.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getBatchAuditTrail.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to get batch audit trail';
      })
      // Search operations
      .addCase(searchBatches.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(searchBatches.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to search batches';
      })
      .addCase(searchAnimals.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(searchAnimals.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to search animals';
      })
      // Export operations
      .addCase(exportAuditTrail.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(exportAuditTrail.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to export audit trail';
      })
      // Para todas las acciones completadas exitosamente que no modifican el estado global
      .addMatcher(
        (action) => action.type.endsWith('/fulfilled') && 
                   !action.type.includes('fetchAnimals') &&
                   !action.type.includes('fetchAnimal') &&
                   !action.type.includes('createAnimal') &&
                   !action.type.includes('updateAnimal') &&
                   !action.type.includes('deleteAnimal') &&
                   !action.type.includes('fetchBatches') &&
                   !action.type.includes('fetchBatch') &&
                   !action.type.includes('createBatch') &&
                   !action.type.includes('fetchStats') &&
                   !action.type.includes('fetchCertificationStandards') &&
                   !action.type.includes('fetchAnimalCertifications') &&
                   !action.type.includes('revokeCertification'),
        (state) => {
          state.loading = false;
        }
      );
  }
});

export const { clearError, clearSelection, selectAnimal, selectBatch } = cattleSlice.actions;
export default cattleSlice.reducer;