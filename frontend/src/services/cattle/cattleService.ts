// src/services/cattle/cattleService.ts
import apiClient from '../apiClient';
import { 
  Animal, 
  AnimalHealthRecord, 
  Batch, 
  CertificationStandard, 
  AnimalCertification,
  AnimalCreateRequest,
  AnimalUpdateRequest,
  AnimalSearchParams,
  AnimalMintRequest,
  AnimalTransferRequest,
  AnimalHealthUpdateRequest,
  BatchCreateRequest,
  BatchStatusUpdateRequest,
  BatchAnimalsUpdateRequest,
  CattleStats,
  BlockchainEvent,
  AuditTrail,
  NFTVerification,
  NFTInfo,
  MintResult,
  TransferResult,
  HealthUpdateResult
} from '../../types/domain/cattle';
import {
  ANIMALS_URL,
  ANIMAL_SEARCH_URL,
  HEALTH_RECORDS_URL,
  BATCHES_URL,
  BATCH_SEARCH_URL,
  CATTLE_STATS_URL,
  CERTIFICATION_STANDARDS_URL,
  ANIMAL_CERTIFICATIONS_URL,
  ANIMAL_MINT_NFT_URL,
  ANIMAL_TRANSFER_URL,
  ANIMAL_UPDATE_HEALTH_URL,
  ANIMAL_VERIFY_NFT_URL,
  ANIMAL_NFT_INFO_URL,
  ANIMAL_HEALTH_RECORDS_URL,
  ANIMAL_BLOCKCHAIN_EVENTS_URL,
  ANIMAL_AUDIT_TRAIL_URL,
  BATCH_UPDATE_STATUS_URL,
  BATCH_ADD_ANIMALS_URL,
  BATCH_REMOVE_ANIMALS_URL,
  BATCH_BLOCKCHAIN_EVENTS_URL,
  BATCH_AUDIT_TRAIL_URL,
  CERTIFICATION_REVOKE_URL,
  AUDIT_TRAIL_EXPORT_URL
} from '../../utils/constants';

class CattleService {
 
  // Animal Management
  async getAnimals(params?: AnimalSearchParams): Promise<{ data: Animal[]; count: number }> {
    const response = await apiClient.get(ANIMALS_URL, { params });
    return response.data;
  }

  async getAnimal(id: number): Promise<Animal> {
    const response = await apiClient.get(`${ANIMALS_URL}${id}/`);
    return response.data;
  }

  async createAnimal(animalData: AnimalCreateRequest): Promise<Animal> {
    const response = await apiClient.post(ANIMALS_URL, animalData);
    return response.data;
  }

  async updateAnimal(id: number, animalData: AnimalUpdateRequest): Promise<Animal> {
    const response = await apiClient.patch(`${ANIMALS_URL}${id}/`, animalData);
    return response.data;
  }

  async deleteAnimal(id: number): Promise<void> {
    await apiClient.delete(`${ANIMALS_URL}${id}/`);
  }

  async searchAnimals(params: AnimalSearchParams): Promise<{ results: Animal[]; count: number }> {
    const response = await apiClient.post(ANIMAL_SEARCH_URL, params);
    return response.data;
  }

  // Animal Actions
  async mintAnimalNFT(animalId: number, mintData: AnimalMintRequest): Promise<MintResult> {
    const response = await apiClient.post(ANIMAL_MINT_NFT_URL(animalId), mintData);
    return response.data;
  }

  async transferAnimal(animalId: number, transferData: AnimalTransferRequest): Promise<TransferResult> {
    const response = await apiClient.post(ANIMAL_TRANSFER_URL(animalId), transferData);
    return response.data;
  }

  async updateAnimalHealth(animalId: number, healthData: AnimalHealthUpdateRequest): Promise<HealthUpdateResult> {
    const response = await apiClient.post(ANIMAL_UPDATE_HEALTH_URL(animalId), healthData);
    return response.data;
  }

  async verifyAnimalNFT(animalId: number): Promise<{
    success: boolean;
    animal_id: number;
    ear_tag: string;
    token_id?: string;
    verification?: NFTVerification;
    error?: string;
  }> {
    const response = await apiClient.get(ANIMAL_VERIFY_NFT_URL(animalId));
    return response.data;
  }

  async getAnimalNFTInfo(animalId: number): Promise<{
    success: boolean;
    animal_id: number;
    ear_tag: string;
    nft_info?: NFTInfo;
    error?: string;
  }> {
    const response = await apiClient.get(ANIMAL_NFT_INFO_URL(animalId));
    return response.data;
  }

  async getAnimalHealthRecords(animalId: number): Promise<AnimalHealthRecord[]> {
    const response = await apiClient.get(ANIMAL_HEALTH_RECORDS_URL(animalId));
    return response.data;
  }

  async getAnimalBlockchainEvents(animalId: number): Promise<BlockchainEvent[]> {
    const response = await apiClient.get(ANIMAL_BLOCKCHAIN_EVENTS_URL(animalId));
    return response.data;
  }

  async getAnimalAuditTrail(animalId: number): Promise<AuditTrail[]> {
    const response = await apiClient.get(ANIMAL_AUDIT_TRAIL_URL(animalId));
    return response.data;
  }

  // Health Records
  async getHealthRecords(params?: {
    animal_id?: number;
    health_status?: string;
    source?: string;
    iot_device?: string;
  }): Promise<AnimalHealthRecord[]> {
    const response = await apiClient.get(HEALTH_RECORDS_URL, { params });
    return response.data;
  }

  async createHealthRecord(recordData: Omit<AnimalHealthRecord, 'id' | 'created_at'>): Promise<AnimalHealthRecord> {
    const response = await apiClient.post(HEALTH_RECORDS_URL, recordData);
    return response.data;
  }

  // Batch Management
  async getBatches(params?: {
    status?: string;
    name?: string;
  }): Promise<Batch[]> {
    const response = await apiClient.get(BATCHES_URL, { params });
    return response.data;
  }

  async getBatch(id: number): Promise<Batch> {
    const response = await apiClient.get(`${BATCHES_URL}${id}/`);
    return response.data;
  }

  async createBatch(batchData: BatchCreateRequest): Promise<Batch> {
    const response = await apiClient.post(BATCHES_URL, batchData);
    return response.data;
  }

  async updateBatchStatus(batchId: number, statusData: BatchStatusUpdateRequest): Promise<{
    success: boolean;
    message: string;
    batch_id: number;
    batch_name: string;
    new_status: string;
    on_blockchain: boolean;
    error?: string;
  }> {
    const response = await apiClient.post(BATCH_UPDATE_STATUS_URL(batchId), statusData);
    return response.data;
  }

  async addAnimalsToBatch(batchId: number, animalsData: BatchAnimalsUpdateRequest): Promise<{
    success: boolean;
    message: string;
    batch_id: number;
    batch_name: string;
    added_animals_count: number;
    error?: string;
  }> {
    const response = await apiClient.post(BATCH_ADD_ANIMALS_URL(batchId), animalsData);
    return response.data;
  }

  async removeAnimalsFromBatch(batchId: number, animalsData: BatchAnimalsUpdateRequest): Promise<{
    success: boolean;
    message: string;
    batch_id: number;
    batch_name: string;
    removed_animals_count: number;
    error?: string;
  }> {
    const response = await apiClient.post(BATCH_REMOVE_ANIMALS_URL(batchId), animalsData);
    return response.data;
  }

  async getBatchBlockchainEvents(batchId: number): Promise<BlockchainEvent[]> {
    const response = await apiClient.get(BATCH_BLOCKCHAIN_EVENTS_URL(batchId));
    return response.data;
  }

  async getBatchAuditTrail(batchId: number): Promise<AuditTrail[]> {
    const response = await apiClient.get(BATCH_AUDIT_TRAIL_URL(batchId));
    return response.data;
  }

  // Certifications
  async getCertificationStandards(): Promise<CertificationStandard[]> {
    const response = await apiClient.get(CERTIFICATION_STANDARDS_URL);
    return response.data;
  }

  async getAnimalCertifications(animalId: number): Promise<AnimalCertification[]> {
    const response = await apiClient.get(ANIMAL_CERTIFICATIONS_URL, {
      params: { animal_id: animalId }
    });
    return response.data;
  }

  async revokeCertification(certificationId: number, reason: string): Promise<{
    success: boolean;
    message: string;
    certification_id: number;
  }> {
    const response = await apiClient.post(CERTIFICATION_REVOKE_URL(certificationId), { reason });
    return response.data;
  }

  // Search endpoints
  async searchBatches(params: {
    name?: string;
    status?: string;
    created_by_id?: number;
    min_animals?: number;
    max_animals?: number;
  }): Promise<{ results: Batch[]; count: number }> {
    const response = await apiClient.post(BATCH_SEARCH_URL, params);
    return response.data;
  }

  // Statistics
  async getCattleStats(): Promise<CattleStats> {
    const response = await apiClient.get(CATTLE_STATS_URL);
    return response.data;
  }

  // Audit Trail
  async exportAuditTrail(format: 'json' | 'csv' = 'json', days: number = 30): Promise<any> {
    const response = await apiClient.get(AUDIT_TRAIL_EXPORT_URL, {
      params: { format, days },
      responseType: format === 'csv' ? 'blob' : 'json'
    });
    return response.data;
  }
}

export const cattleService = new CattleService();