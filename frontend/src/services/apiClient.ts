// src/services/apiClient.ts
import axios from 'axios';
import { authService } from './auth/authService';
import { 
  API_BASE_URL, 
  JWT_ACCESS_TOKEN_KEY, 
  JWT_REFRESH_TOKEN_KEY 
} from '../auth/permissions/constants';

// Crear instancia de axios
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: parseInt(import.meta.env.VITE_API_TIMEOUT || '10000'),
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token a las requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(JWT_ACCESS_TOKEN_KEY);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar respuestas y errores
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Si el error es 401 y no hemos intentado refrescar el token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Intentar refrescar el token
        await authService.refreshToken();
        const newToken = localStorage.getItem(JWT_ACCESS_TOKEN_KEY);
        
        // Reintentar la request original con el nuevo token
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Si el refresh falla, hacer logout y redirigir al login
        authService.logout();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    // Manejar otros errores de autenticación
    if (error.response?.status === 401) {
      localStorage.removeItem(JWT_ACCESS_TOKEN_KEY);
      localStorage.removeItem(JWT_REFRESH_TOKEN_KEY);
      window.location.href = '/login';
    }

    // Log de errores del servidor
    if (error.response?.status >= 500) {
      console.error('Server Error:', error.response.data);
    }

    return Promise.reject(error);
  }
);

// Función para manejar downloads de archivos (CSV, etc.)
export const downloadFile = async (url: string, filename: string) => {
  const response = await apiClient.get(url, {
    responseType: 'blob',
  });
  
  const blob = new Blob([response.data]);
  const downloadUrl = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = downloadUrl;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(downloadUrl);
};

export default apiClient;