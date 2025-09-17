// src/services/cattle/certificationService.ts
import apiClient from '../apiClient';
import { 
  CertificationStandard, 
  AnimalCertification, 
  CertificationCreateRequest,
  CertificationUpdateRequest
} from '../../types/domain/cattle';

class CertificationService {
  private baseURL: string;

  constructor() {
    this.baseURL = '/api/cattle';
  }

  // Certification Standards
  async getCertificationStandards(): Promise<CertificationStandard[]> {
    const response = await apiClient.get(`${this.baseURL}/certification-standards/`);
    return response.data;
  }

  async getCertificationStandard(id: number): Promise<CertificationStandard> {
    const response = await apiClient.get(`${this.baseURL}/certification-standards/${id}/`);
    return response.data;
  }

  async createCertificationStandard(standardData: Omit<CertificationStandard, 'id' | 'created_at' | 'updated_at'>): Promise<CertificationStandard> {
    const response = await apiClient.post(`${this.baseURL}/certification-standards/`, standardData);
    return response.data;
  }

  async updateCertificationStandard(id: number, standardData: Partial<CertificationStandard>): Promise<CertificationStandard> {
    const response = await apiClient.patch(`${this.baseURL}/certification-standards/${id}/`, standardData);
    return response.data;
  }

  async deleteCertificationStandard(id: number): Promise<void> {
    await apiClient.delete(`${this.baseURL}/certification-standards/${id}/`);
  }

  // Animal Certifications
  async getAnimalCertifications(animalId?: number): Promise<AnimalCertification[]> {
    const params = animalId ? { animal_id: animalId } : {};
    const response = await apiClient.get(`${this.baseURL}/animal-certifications/`, { params });
    return response.data;
  }

  async getAnimalCertification(id: number): Promise<AnimalCertification> {
    const response = await apiClient.get(`${this.baseURL}/animal-certifications/${id}/`);
    return response.data;
  }

  async createAnimalCertification(certificationData: CertificationCreateRequest): Promise<AnimalCertification> {
    const response = await apiClient.post(`${this.baseURL}/animal-certifications/`, certificationData);
    return response.data;
  }

  async updateAnimalCertification(id: number, certificationData: CertificationUpdateRequest): Promise<AnimalCertification> {
    const response = await apiClient.patch(`${this.baseURL}/animal-certifications/${id}/`, certificationData);
    return response.data;
  }

  async revokeCertification(id: number, reason: string): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.post(`${this.baseURL}/animal-certifications/${id}/revoke/`, { reason });
    return response.data;
  }

  async deleteAnimalCertification(id: number): Promise<void> {
    await apiClient.delete(`${this.baseURL}/animal-certifications/${id}/`);
  }

  // Bulk operations
  async bulkCreateCertifications(certificationsData: CertificationCreateRequest[]): Promise<AnimalCertification[]> {
    const response = await apiClient.post(`${this.baseURL}/animal-certifications/bulk/`, {
      certifications: certificationsData
    });
    return response.data;
  }

  async getExpiringCertifications(days: number = 30): Promise<AnimalCertification[]> {
    const response = await apiClient.get(`${this.baseURL}/animal-certifications/expiring/`, {
      params: { days }
    });
    return response.data;
  }
}

export const certificationService = new CertificationService();