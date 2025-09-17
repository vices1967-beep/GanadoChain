// src/contexts/cattle/CattleContext.tsx
import React, { createContext, useContext, ReactNode } from 'react';
import { useCattle } from '../../hooks/cattle/useCattle';

interface CattleContextType {
  loading: boolean;
  error: string | null;
  clearError: () => void;
  
  // Animal methods
  getAnimals: (params?: any) => Promise<any>;
  getAnimal: (id: number) => Promise<any>;
  createAnimal: (animalData: any) => Promise<any>;
  updateAnimal: (id: number, animalData: any) => Promise<any>;
  deleteAnimal: (id: number) => Promise<void>;
  searchAnimals: (params: any) => Promise<any>;
  mintAnimalNFT: (animalId: number, mintData: any) => Promise<any>;
  transferAnimal: (animalId: number, transferData: any) => Promise<any>;
  updateAnimalHealth: (animalId: number, healthData: any) => Promise<any>;
  verifyAnimalNFT: (animalId: number) => Promise<any>;
  getAnimalNFTInfo: (animalId: number) => Promise<any>;
  getAnimalHealthRecords: (animalId: number) => Promise<any>;
  getAnimalBlockchainEvents: (animalId: number) => Promise<any>;
  getAnimalAuditTrail: (animalId: number) => Promise<any>;
  
  // Batch methods
  getBatches: (params?: any) => Promise<any>;
  getBatch: (id: number) => Promise<any>;
  createBatch: (batchData: any) => Promise<any>;
  updateBatchStatus: (batchId: number, statusData: any) => Promise<any>;
  addAnimalsToBatch: (batchId: number, animalsData: any) => Promise<any>;
  removeAnimalsFromBatch: (batchId: number, animalsData: any) => Promise<any>;
  getBatchBlockchainEvents: (batchId: number) => Promise<any>;
  getBatchAuditTrail: (batchId: number) => Promise<any>;
  searchBatches: (params: any) => Promise<any>;
  
  // Certification methods
  getCertificationStandards: () => Promise<any>;
  getAnimalCertifications: (animalId: number) => Promise<any>;
  revokeCertification: (certificationId: number, reason: string) => Promise<any>;
  
  // Stats and audit
  getStats: () => Promise<any>;
  exportAuditTrail: (format?: 'json' | 'csv', days?: number) => Promise<any>;
}

const CattleContext = createContext<CattleContextType | undefined>(undefined);

export const useCattleContext = () => {
  const context = useContext(CattleContext);
  if (context === undefined) {
    throw new Error('useCattleContext must be used within a CattleProvider');
  }
  return context;
};

interface CattleProviderProps {
  children: ReactNode;
}

export const CattleProvider: React.FC<CattleProviderProps> = ({ children }) => {
  const cattle = useCattle();

  return (
    <CattleContext.Provider value={cattle}>
      {children}
    </CattleContext.Provider>
  );
};