import axios from 'axios';
import {
  API_BASE_URL,
  API_TIMEOUT,
  JWT_ACCESS_TOKEN_KEY,
  JWT_REFRESH_TOKEN_KEY,
  LOGIN_URL,
  REFRESH_TOKEN_URL,
  REGISTER_URL,
  WALLET_CONNECT_URL,
  USER_PROFILE_URL
} from '../../utils/constants';

const API_URL = API_BASE_URL;

// Configuración base de axios
const api = axios.create({
  baseURL: API_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar el token a las requests
api.interceptors.request.use(
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

// Interceptor para manejar errores de autenticación
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem(JWT_REFRESH_TOKEN_KEY);
        if (refreshToken) {
          const response = await api.post(REFRESH_TOKEN_URL, {
            refresh: refreshToken
          });
          
          const { access } = response.data;
          localStorage.setItem(JWT_ACCESS_TOKEN_KEY, access);
          
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        localStorage.removeItem(JWT_ACCESS_TOKEN_KEY);
        localStorage.removeItem(JWT_REFRESH_TOKEN_KEY);
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export interface LoginData {
  username: string;
  password: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user?: User;
}

export interface WalletConnectData {
  wallet_address: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  wallet_address?: string;
  is_active: boolean;
  date_joined: string;
}

export const authService = {
  async login(credentials: LoginData): Promise<LoginResponse> {
    const response = await api.post(LOGIN_URL, credentials);
    
    // Guardar tokens
    if (response.data.access) {
      localStorage.setItem(JWT_ACCESS_TOKEN_KEY, response.data.access);
    }
    if (response.data.refresh) {
      localStorage.setItem(JWT_REFRESH_TOKEN_KEY, response.data.refresh);
    }
    
    return response.data;
  },

  async refreshToken(): Promise<{ access: string }> {
    const refreshToken = localStorage.getItem(JWT_REFRESH_TOKEN_KEY);
    
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await api.post(REFRESH_TOKEN_URL, {
      refresh: refreshToken
    });

    if (response.data.access) {
      localStorage.setItem(JWT_ACCESS_TOKEN_KEY, response.data.access);
    }

    return response.data;
  },
  async register(userData: any): Promise<any> {
    const response = await api.post(REGISTER_URL, userData);
    return response.data;
  },

  async connectWallet(walletData: WalletConnectData): Promise<any> {
    const response = await api.post(WALLET_CONNECT_URL, walletData);
    return response.data;
  },

  async getProfile(): Promise<User> {
    const response = await api.get(USER_PROFILE_URL);
    return response.data;
  },

  logout(): void {
    localStorage.removeItem(JWT_ACCESS_TOKEN_KEY);
    localStorage.removeItem(JWT_REFRESH_TOKEN_KEY);
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem(JWT_ACCESS_TOKEN_KEY);
  },

  getAccessToken(): string | null {
    return localStorage.getItem(JWT_ACCESS_TOKEN_KEY);
  },

  getRefreshToken(): string | null {
    return localStorage.getItem(JWT_REFRESH_TOKEN_KEY);
  },
};

export default api;