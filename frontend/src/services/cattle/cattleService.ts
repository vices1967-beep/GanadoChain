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
  NFTInfo
} from '../../types/domain/cattle';

class CattleService {
  private baseURL: string;

  constructor() {
    this.baseURL = '/api/cattle';
  }

  // Animal Management
  async getAnimals(params?: AnimalSearchParams): Promise<{ data: Animal[]; count: number }> {
    const response = await apiClient.get(`${this.baseURL}/animals/`, { params });
    return response.data;
  }

  async getAnimal(id: number): Promise<Animal> {
    const response = await apiClient.get(`${this.baseURL}/animals/${id}/`);
    return response.data;
  }

  async createAnimal(animalData: AnimalCreateRequest): Promise<Animal> {
    const response = await apiClient.post(`${this.baseURL}/animals/`, animalData);
    return response.data;
  }

  async updateAnimal(id: number, animalData: AnimalUpdateRequest): Promise<Animal> {
    const response = await apiClient.patch(`${this.baseURL}/animals/${id}/`, animalData);
    return response.data;
  }

  async deleteAnimal(id: number): Promise<void> {
    await apiClient.delete(`${this.baseURL}/animals/${id}/`);
  }

  async searchAnimals(params: AnimalSearchParams): Promise<{ results: Animal[]; count: number }> {
    const response = await apiClient.post(`${this.baseURL}/animals/search/`, params);
    return response.data;
  }

  // Animal Actions
  async mintAnimalNFT(animalId: number, mintData: AnimalMintRequest): Promise<{
    success: boolean;
    message: string;
    animal_id: number;
    ear_tag: string;
    token_id?: string;
    transaction_hash?: string;
    owner_wallet?: string;
    nft_owner_wallet?: string;
    mint_transaction_hash?: string;
    error?: string;
  }> {
    const response = await apiClient.post(`${this.baseURL}/animals/${animalId}/mint_nft/`, mintData);
    return response.data;
  }

  async transferAnimal(animalId: number, transferData: AnimalTransferRequest): Promise<{
    success: boolean;
    message: string;
    transaction_hash?: string;
    error?: string;
  }> {
    const response = await apiClient.post(`${this.baseURL}/animals/${animalId}/transfer/`, transferData);
    return response.data;
  }

  async updateAnimalHealth(animalId: number, healthData: AnimalHealthUpdateRequest): Promise<{
    success: boolean;
    message: string;
    health_record_id?: number;
    error?: string;
  }> {
    const response = await apiClient.post(`${this.baseURL}/animals/${animalId}/update_health/`, healthData);
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
    const response = await apiClient.get(`${this.baseURL}/animals/${animalId}/verify_nft/`);
    return response.data;
  }

  async getAnimalNFTInfo(animalId: number): Promise<{
    success: boolean;
    animal_id: number;
    ear_tag: string;
    nft_info?: NFTInfo;
    error?: string;
  }> {
    const response = await apiClient.get(`${this.baseURL}/animals/${animalId}/nft_info/`);
    return response.data;
  }

  async getAnimalHealthRecords(animalId: number): Promise<AnimalHealthRecord[]> {
    const response = await apiClient.get(`${this.baseURL}/animals/${animalId}/health_records/`);
    return response.data;
  }

  async getAnimalBlockchainEvents(animalId: number): Promise<BlockchainEvent[]> {
    const response = await apiClient.get(`${this.baseURL}/animals/${animalId}/blockchain_events/`);
    return response.data;
  }

  async getAnimalAuditTrail(animalId: number): Promise<AuditTrail[]> {
    const response = await apiClient.get(`${this.baseURL}/animals/${animalId}/audit_trail/`);
    return response.data;
  }

  // Health Records
  async getHealthRecords(params?: {
    animal_id?: number;
    health_status?: string;
    source?: string;
    iot_device?: string;
  }): Promise<AnimalHealthRecord[]> {
    const response = await apiClient.get(`${this.baseURL}/health-records/`, { params });
    return response.data;
  }

  async createHealthRecord(recordData: Omit<AnimalHealthRecord, 'id' | 'created_at'>): Promise<AnimalHealthRecord> {
    const response = await apiClient.post(`${this.baseURL}/health-records/`, recordData);
    return response.data;
  }

  // Batch Management
  async getBatches(params?: {
    status?: string;
    name?: string;
  }): Promise<Batch[]> {
    const response = await apiClient.get(`${this.baseURL}/batches/`, { params });
    return response.data;
  }

  async getBatch(id: number): Promise<Batch> {
    const response = await apiClient.get(`${this.baseURL}/batches/${id}/`);
    return response.data;
  }

  async createBatch(batchData: BatchCreateRequest): Promise<Batch> {
    const response = await apiClient.post(`${this.baseURL}/batches/`, batchData);
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
    const response = await apiClient.post(`${this.baseURL}/batches/${batchId}/update_status/`, statusData);
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
    const response = await apiClient.post(`${this.baseURL}/batches/${batchId}/add_animals/`, animalsData);
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
    const response = await apiClient.post(`${this.baseURL}/batches/${batchId}/remove_animals/`, animalsData);
    return response.data;
  }

  async getBatchBlockchainEvents(batchId: number): Promise<BlockchainEvent[]> {
    const response = await apiClient.get(`${this.baseURL}/batches/${batchId}/blockchain_events/`);
    return response.data;
  }

  async getBatchAuditTrail(batchId: number): Promise<AuditTrail[]> {
    const response = await apiClient.get(`${this.baseURL}/batches/${batchId}/audit_trail/`);
    return response.data;
  }

  // Certifications
  async getCertificationStandards(): Promise<CertificationStandard[]> {
    const response = await apiClient.get(`${this.baseURL}/certification-standards/`);
    return response.data;
  }

  async getAnimalCertifications(animalId: number): Promise<AnimalCertification[]> {
    const response = await apiClient.get(`${this.baseURL}/animal-certifications/`, {
      params: { animal_id: animalId }
    });
    return response.data;
  }

  async revokeCertification(certificationId: number, reason: string): Promise<{
    success: boolean;
    message: string;
    certification_id: number;
  }> {
    const response = await apiClient.post(`${this.baseURL}/animal-certifications/${certificationId}/revoke/`, {
      reason
    });
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
    const response = await apiClient.post(`${this.baseURL}/batches/search/`, params);
    return response.data;
  }

  // Statistics
  async getCattleStats(): Promise<CattleStats> {
    const response = await apiClient.get(`${this.baseURL}/stats/`);
    return response.data;
  }

  // Audit Trail
  async exportAuditTrail(format: 'json' | 'csv' = 'json', days: number = 30): Promise<any> {
    const response = await apiClient.get(`${this.baseURL}/audit/export/`, {
      params: { format, days },
      responseType: format === 'csv' ? 'blob' : 'json'
    });
    return response.data;
  }
}

export const cattleService = new CattleService();