// src/types/services/apiClient.ts
import { AxiosInstance } from 'axios';

declare const apiClient: AxiosInstance & {
  downloadFile?: (url: string, filename: string) => Promise<void>;
};

export default apiClient;
export { apiClient };