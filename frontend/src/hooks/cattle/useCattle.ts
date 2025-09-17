// src/hooks/cattle/useCattle.ts
import { useState, useCallback } from 'react';
import { cattleService } from '../../services/cattle/cattleService';
import { getErrorMessage } from '../../utils/errors';
import { 
  AnimalCreateRequest, 
  AnimalUpdateRequest, 
  AnimalSearchParams,
  AnimalMintRequest,
  AnimalTransferRequest,
  AnimalHealthUpdateRequest,
  BatchCreateRequest,
  BatchStatusUpdateRequest,
  BatchAnimalsUpdateRequest
} from '../../types/domain/cattle';

export const useCattle = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const wrapOperation = async <T>(operation: () => Promise<T>): Promise<T> => {
    setLoading(true);
    setError(null);
    try {
      return await operation();
    } catch (err: any) {
      const errorMessage = getErrorMessage(err);
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Animal operations
  const getAnimals = useCallback((params?: AnimalSearchParams) => 
    wrapOperation(() => cattleService.getAnimals(params)), []);

  const getAnimal = useCallback((id: number) => 
    wrapOperation(() => cattleService.getAnimal(id)), []);

  const createAnimal = useCallback((animalData: AnimalCreateRequest) => 
    wrapOperation(() => cattleService.createAnimal(animalData)), []);

  const updateAnimal = useCallback((id: number, animalData: AnimalUpdateRequest) => 
    wrapOperation(() => cattleService.updateAnimal(id, animalData)), []);

  const deleteAnimal = useCallback((id: number) => 
    wrapOperation(() => cattleService.deleteAnimal(id)), []);

  const searchAnimals = useCallback((params: AnimalSearchParams) => 
    wrapOperation(() => cattleService.searchAnimals(params)), []);

  // Animal actions
  const mintAnimalNFT = useCallback((animalId: number, mintData: AnimalMintRequest) => 
    wrapOperation(() => cattleService.mintAnimalNFT(animalId, mintData)), []);

  const transferAnimal = useCallback((animalId: number, transferData: AnimalTransferRequest) => 
    wrapOperation(() => cattleService.transferAnimal(animalId, transferData)), []);

  const updateAnimalHealth = useCallback((animalId: number, healthData: AnimalHealthUpdateRequest) => 
    wrapOperation(() => cattleService.updateAnimalHealth(animalId, healthData)), []);

  const verifyAnimalNFT = useCallback((animalId: number) => 
    wrapOperation(() => cattleService.verifyAnimalNFT(animalId)), []);

  const getAnimalNFTInfo = useCallback((animalId: number) => 
    wrapOperation(() => cattleService.getAnimalNFTInfo(animalId)), []);

  const getAnimalHealthRecords = useCallback((animalId: number) => 
    wrapOperation(() => cattleService.getAnimalHealthRecords(animalId)), []);

  const getAnimalBlockchainEvents = useCallback((animalId: number) => 
    wrapOperation(() => cattleService.getAnimalBlockchainEvents(animalId)), []);

  const getAnimalAuditTrail = useCallback((animalId: number) => 
    wrapOperation(() => cattleService.getAnimalAuditTrail(animalId)), []);

  // Batch operations
  const getBatches = useCallback((params?: any) => 
    wrapOperation(() => cattleService.getBatches(params)), []);

  const getBatch = useCallback((id: number) => 
    wrapOperation(() => cattleService.getBatch(id)), []);

  const createBatch = useCallback((batchData: BatchCreateRequest) => 
    wrapOperation(() => cattleService.createBatch(batchData)), []);

  const updateBatchStatus = useCallback((batchId: number, statusData: BatchStatusUpdateRequest) => 
    wrapOperation(() => cattleService.updateBatchStatus(batchId, statusData)), []);

  const addAnimalsToBatch = useCallback((batchId: number, animalsData: BatchAnimalsUpdateRequest) => 
    wrapOperation(() => cattleService.addAnimalsToBatch(batchId, animalsData)), []);

  const removeAnimalsFromBatch = useCallback((batchId: number, animalsData: BatchAnimalsUpdateRequest) => 
    wrapOperation(() => cattleService.removeAnimalsFromBatch(batchId, animalsData)), []);

  const getBatchBlockchainEvents = useCallback((batchId: number) => 
    wrapOperation(() => cattleService.getBatchBlockchainEvents(batchId)), []);

  const getBatchAuditTrail = useCallback((batchId: number) => 
    wrapOperation(() => cattleService.getBatchAuditTrail(batchId)), []);

  // Search and stats
  const searchBatches = useCallback((params: any) => 
    wrapOperation(() => cattleService.searchBatches(params)), []);

  const getStats = useCallback(() => 
    wrapOperation(() => cattleService.getCattleStats()), []);

  // Certifications
  const getCertificationStandards = useCallback(() => 
    wrapOperation(() => cattleService.getCertificationStandards()), []);

  const getAnimalCertifications = useCallback((animalId: number) => 
    wrapOperation(() => cattleService.getAnimalCertifications(animalId)), []);

  const revokeCertification = useCallback((certificationId: number, reason: string) => 
    wrapOperation(() => cattleService.revokeCertification(certificationId, reason)), []);

  // Audit trail
  const exportAuditTrail = useCallback((format: 'json' | 'csv' = 'json', days: number = 30) => 
    wrapOperation(() => cattleService.exportAuditTrail(format, days)), []);

  return {
    loading,
    error,
    clearError: () => setError(null),
    
    // Animal methods
    getAnimals,
    getAnimal,
    createAnimal,
    updateAnimal,
    deleteAnimal,
    searchAnimals,
    mintAnimalNFT,
    transferAnimal,
    updateAnimalHealth,
    verifyAnimalNFT,
    getAnimalNFTInfo,
    getAnimalHealthRecords,
    getAnimalBlockchainEvents,
    getAnimalAuditTrail,
    
    // Batch methods
    getBatches,
    getBatch,
    createBatch,
    updateBatchStatus,
    addAnimalsToBatch,
    removeAnimalsFromBatch,
    getBatchBlockchainEvents,
    getBatchAuditTrail,
    searchBatches,
    
    // Certification methods
    getCertificationStandards,
    getAnimalCertifications,
    revokeCertification,
    
    // Stats and audit
    getStats,
    exportAuditTrail
  };
};