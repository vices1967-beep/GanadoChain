// src/stores/slices/cattle.slice.ts
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { cattleService } from '../../services/cattle/cattleService';
import { Animal, Batch, AnimalCertification, CattleStats } from '../../types/domain/cattle';

interface CattleState {
  animals: Animal[];
  batches: Batch[];
  certifications: AnimalCertification[];
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
      });
  }
});

export const { clearError, clearSelection, selectAnimal, selectBatch } = cattleSlice.actions;
export default cattleSlice.reducer;