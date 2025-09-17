// src/services/cattle/auditService.ts
import { downloadFile } from '../apiClient';
import apiClient from '../apiClient';
import { AuditTrail, AuditExportRequest, AuditStats } from '../../types/domain/cattle';

class AuditService {
  private baseURL: string;

  constructor() {
    this.baseURL = '/api/cattle';
  }

  async getAuditTrail(params?: {
    object_type?: string;
    object_id?: string;
    action_type?: string;
    user_id?: number;
    start_date?: string;
    end_date?: string;
    page?: number;
    page_size?: number;
  }): Promise<{ results: AuditTrail[]; count: number }> {
    const response = await apiClient.get(`${this.baseURL}/audit/`, { params });
    return response.data;
  }

  async getAuditTrailByObject(objectType: string, objectId: string): Promise<AuditTrail[]> {
    const response = await apiClient.get(`${this.baseURL}/audit/${objectType}/${objectId}/`);
    return response.data;
  }

  async getAuditStats(): Promise<AuditStats> {
    const response = await apiClient.get(`${this.baseURL}/audit/stats/`);
    return response.data;
  }

  async exportAuditTrail(exportRequest: AuditExportRequest): Promise<void> {
    const { format, days, object_type, object_id, action_type } = exportRequest;
    
    const params = new URLSearchParams();
    params.append('format', format);
    if (days) params.append('days', days.toString());
    if (object_type) params.append('object_type', object_type);
    if (object_id) params.append('object_id', object_id);
    if (action_type) params.append('action_type', action_type);

    const filename = `audit_export_${new Date().toISOString().split('T')[0]}.${format}`;
    
    await downloadFile(`${this.baseURL}/audit/export/?${params.toString()}`, filename);
  }

  async searchAuditTrail(query: string): Promise<AuditTrail[]> {
    const response = await apiClient.get(`${this.baseURL}/audit/search/`, {
      params: { q: query }
    });
    return response.data;
  }

  async getRecentActivity(limit: number = 10): Promise<AuditTrail[]> {
    const response = await apiClient.get(`${this.baseURL}/audit/recent/`, {
      params: { limit }
    });
    return response.data;
  }
}

export const auditService = new AuditService();