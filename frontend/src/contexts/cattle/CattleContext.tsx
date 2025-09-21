// src/contexts/cattle/CattleContext.tsx (versión completa corregida)
import React, { createContext, useContext, ReactNode, useReducer } from 'react';
import { Animal, Batch, AnimalCertification, CattleStats, CertificationStandard } from '../../types/domain/cattle';
import { useCattle } from '../../hooks/cattle/useCattle';

interface CattleState {
  animals: Animal[];
  batches: Batch[];
  certifications: AnimalCertification[];
  certificationStandards: CertificationStandard[]; // ← AÑADIDO
  stats: CattleStats | null;
  selectedAnimal: Animal | null;
  selectedBatch: Batch | null;
  loading: boolean;
  error: string | null;
}

interface CattleContextType extends CattleState {
  // Animal methods
  getAnimals: (params?: any) => Promise<void>;
  getAnimal: (id: number) => Promise<void>;
  createAnimal: (animalData: any) => Promise<void>;
  updateAnimal: (id: number, animalData: any) => Promise<void>;
  deleteAnimal: (id: number) => Promise<void>;
  searchAnimals: (params: any) => Promise<void>;
  mintAnimalNFT: (animalId: number, mintData: any) => Promise<void>;
  transferAnimal: (animalId: number, transferData: any) => Promise<void>;
  updateAnimalHealth: (animalId: number, healthData: any) => Promise<void>;
  verifyAnimalNFT: (animalId: number) => Promise<void>;
  getAnimalNFTInfo: (animalId: number) => Promise<void>;
  getAnimalHealthRecords: (animalId: number) => Promise<void>;
  getAnimalBlockchainEvents: (animalId: number) => Promise<void>;
  getAnimalAuditTrail: (animalId: number) => Promise<void>;
  
  // Batch methods
  getBatches: (params?: any) => Promise<void>;
  getBatch: (id: number) => Promise<void>;
  createBatch: (batchData: any) => Promise<void>;
  updateBatchStatus: (batchId: number, statusData: any) => Promise<void>;
  addAnimalsToBatch: (batchId: number, animalsData: any) => Promise<void>;
  removeAnimalsFromBatch: (batchId: number, animalsData: any) => Promise<void>;
  getBatchBlockchainEvents: (batchId: number) => Promise<void>;
  getBatchAuditTrail: (batchId: number) => Promise<void>;
  searchBatches: (params: any) => Promise<void>;
  
  // Certification methods
  getCertificationStandards: () => Promise<void>;
  getAnimalCertifications: (animalId: number) => Promise<void>;
  revokeCertification: (certificationId: number, reason: string) => Promise<void>;
  
  // Stats and audit
  getStats: () => Promise<void>;
  exportAuditTrail: (format?: 'json' | 'csv', days?: number) => Promise<void>;
  
  // Utility methods
  clearError: () => void;
  clearSelection: () => void;
}

const CattleContext = createContext<CattleContextType | undefined>(undefined);

// Tipos de acciones para el reducer
type CattleAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_ANIMALS'; payload: Animal[] }
  | { type: 'ADD_ANIMAL'; payload: Animal }
  | { type: 'UPDATE_ANIMAL'; payload: Animal }
  | { type: 'REMOVE_ANIMAL'; payload: number }
  | { type: 'SET_BATCHES'; payload: Batch[] }
  | { type: 'ADD_BATCH'; payload: Batch }
  | { type: 'UPDATE_BATCH'; payload: Batch }
  | { type: 'SET_CERTIFICATIONS'; payload: AnimalCertification[] }
  | { type: 'SET_CERTIFICATION_STANDARDS'; payload: CertificationStandard[] } // ← AÑADIDO
  | { type: 'SET_STATS'; payload: CattleStats }
  | { type: 'SELECT_ANIMAL'; payload: Animal | null }
  | { type: 'SELECT_BATCH'; payload: Batch | null }
  | { type: 'CLEAR_ERROR' }
  | { type: 'CLEAR_SELECTION' };

// Reducer para manejar el estado
const cattleReducer = (state: CattleState, action: CattleAction): CattleState => {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload, loading: false };
    case 'SET_ANIMALS':
      return { ...state, animals: action.payload, loading: false };
    case 'ADD_ANIMAL':
      return { ...state, animals: [...state.animals, action.payload], loading: false };
    case 'UPDATE_ANIMAL':
      return {
        ...state,
        animals: state.animals.map(animal =>
          animal.id === action.payload.id ? action.payload : animal
        ),
        loading: false
      };
    case 'REMOVE_ANIMAL':
      return {
        ...state,
        animals: state.animals.filter(animal => animal.id !== action.payload),
        loading: false
      };
    case 'SET_BATCHES':
      return { ...state, batches: action.payload, loading: false };
    case 'ADD_BATCH':
      return { ...state, batches: [...state.batches, action.payload], loading: false };
    case 'UPDATE_BATCH':
      return {
        ...state,
        batches: state.batches.map(batch =>
          batch.id === action.payload.id ? action.payload : batch
        ),
        loading: false
      };
    case 'SET_CERTIFICATIONS':
      return { ...state, certifications: action.payload, loading: false };
    case 'SET_CERTIFICATION_STANDARDS': // ← AÑADIDO
      return { ...state, certificationStandards: action.payload, loading: false };
    case 'SET_STATS':
      return { ...state, stats: action.payload, loading: false };
    case 'SELECT_ANIMAL':
      return { ...state, selectedAnimal: action.payload };
    case 'SELECT_BATCH':
      return { ...state, selectedBatch: action.payload };
    case 'CLEAR_ERROR':
      return { ...state, error: null };
    case 'CLEAR_SELECTION':
      return { ...state, selectedAnimal: null, selectedBatch: null };
    default:
      return state;
  }
};

const initialState: CattleState = {
  animals: [],
  batches: [],
  certifications: [],
  certificationStandards: [], // ← AÑADIDO
  stats: null,
  selectedAnimal: null,
  selectedBatch: null,
  loading: false,
  error: null
};

interface CattleProviderProps {
  children: ReactNode;
}

export const CattleProvider: React.FC<CattleProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(cattleReducer, initialState);
  const cattleHook = useCattle();

  // Función wrapper para manejar operaciones con estado
  const withLoadingAndError = async <T,>(
    operation: () => Promise<T>,
    successAction?: (result: T) => void
  ): Promise<void> => {
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      const result = await operation();
      if (successAction) {
        successAction(result);
      }
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: cattleHook.error });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const contextValue: CattleContextType = {
    ...state,
    
    // Animal methods
    getAnimals: (params?: any) => 
      withLoadingAndError(() => cattleHook.getAnimals(params), (response) => {
        dispatch({ type: 'SET_ANIMALS', payload: response.data });
      }),

    getAnimal: (id: number) => 
      withLoadingAndError(() => cattleHook.getAnimal(id), (animal) => {
        dispatch({ type: 'SELECT_ANIMAL', payload: animal });
      }),

    createAnimal: (animalData: any) => 
      withLoadingAndError(() => cattleHook.createAnimal(animalData), (newAnimal) => {
        dispatch({ type: 'ADD_ANIMAL', payload: newAnimal });
      }),

    updateAnimal: (id: number, animalData: any) => 
      withLoadingAndError(() => cattleHook.updateAnimal(id, animalData), (updatedAnimal) => {
        dispatch({ type: 'UPDATE_ANIMAL', payload: updatedAnimal });
      }),

    deleteAnimal: (id: number) => 
      withLoadingAndError(() => cattleHook.deleteAnimal(id), () => {
        dispatch({ type: 'REMOVE_ANIMAL', payload: id });
      }),

    searchAnimals: (params: any) => 
      withLoadingAndError(() => cattleHook.searchAnimals(params), (response) => {
        dispatch({ type: 'SET_ANIMALS', payload: response.results });
      }),

    mintAnimalNFT: (animalId: number, mintData: any) => 
      withLoadingAndError(() => cattleHook.mintAnimalNFT(animalId, mintData)),

    transferAnimal: (animalId: number, transferData: any) => 
      withLoadingAndError(() => cattleHook.transferAnimal(animalId, transferData)),

    updateAnimalHealth: (animalId: number, healthData: any) => 
      withLoadingAndError(() => cattleHook.updateAnimalHealth(animalId, healthData)),

    verifyAnimalNFT: (animalId: number) => 
      withLoadingAndError(() => cattleHook.verifyAnimalNFT(animalId)),

    getAnimalNFTInfo: (animalId: number) => 
      withLoadingAndError(() => cattleHook.getAnimalNFTInfo(animalId)),

    getAnimalHealthRecords: (animalId: number) => 
      withLoadingAndError(() => cattleHook.getAnimalHealthRecords(animalId)),

    getAnimalBlockchainEvents: (animalId: number) => 
      withLoadingAndError(() => cattleHook.getAnimalBlockchainEvents(animalId)),

    getAnimalAuditTrail: (animalId: number) => 
      withLoadingAndError(() => cattleHook.getAnimalAuditTrail(animalId)),

    // Batch methods
    getBatches: (params?: any) => 
      withLoadingAndError(() => cattleHook.getBatches(params), (batches) => {
        dispatch({ type: 'SET_BATCHES', payload: batches });
      }),

    getBatch: (id: number) => 
      withLoadingAndError(() => cattleHook.getBatch(id), (batch) => {
        dispatch({ type: 'SELECT_BATCH', payload: batch });
      }),

    createBatch: (batchData: any) => 
      withLoadingAndError(() => cattleHook.createBatch(batchData), (newBatch) => {
        dispatch({ type: 'ADD_BATCH', payload: newBatch });
      }),

    updateBatchStatus: (batchId: number, statusData: any) => 
      withLoadingAndError(() => cattleHook.updateBatchStatus(batchId, statusData)),

    addAnimalsToBatch: (batchId: number, animalsData: any) => 
      withLoadingAndError(() => cattleHook.addAnimalsToBatch(batchId, animalsData)),

    removeAnimalsFromBatch: (batchId: number, animalsData: any) => 
      withLoadingAndError(() => cattleHook.removeAnimalsFromBatch(batchId, animalsData)),

    getBatchBlockchainEvents: (batchId: number) => 
      withLoadingAndError(() => cattleHook.getBatchBlockchainEvents(batchId)),

    getBatchAuditTrail: (batchId: number) => 
      withLoadingAndError(() => cattleHook.getBatchAuditTrail(batchId)),

    searchBatches: (params: any) => 
      withLoadingAndError(() => cattleHook.searchBatches(params)),

    // Certification methods
    getCertificationStandards: () => 
      withLoadingAndError(() => cattleHook.getCertificationStandards(), (standards) => {
        dispatch({ type: 'SET_CERTIFICATION_STANDARDS', payload: standards });
      }),

    getAnimalCertifications: (animalId: number) => 
      withLoadingAndError(() => cattleHook.getAnimalCertifications(animalId), (certs) => {
        dispatch({ type: 'SET_CERTIFICATIONS', payload: certs });
      }),

    revokeCertification: (certificationId: number, reason: string) => 
      withLoadingAndError(() => cattleHook.revokeCertification(certificationId, reason)),

    // Stats and audit
    getStats: () => 
      withLoadingAndError(() => cattleHook.getStats(), (stats) => {
        dispatch({ type: 'SET_STATS', payload: stats });
      }),

    exportAuditTrail: (format?: 'json' | 'csv', days?: number) => 
      withLoadingAndError(() => cattleHook.exportAuditTrail(format, days)),

    // Utility methods
    clearError: () => dispatch({ type: 'CLEAR_ERROR' }),
    clearSelection: () => dispatch({ type: 'CLEAR_SELECTION' })
  };

  return (
    <CattleContext.Provider value={contextValue}>
      {children}
    </CattleContext.Provider>
  );
};

export const useCattleContext = () => {
  const context = useContext(CattleContext);
  if (context === undefined) {
    throw new Error('useCattleContext must be used within a CattleProvider');
  }
  return context;
};