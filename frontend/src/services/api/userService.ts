// src/services/api/userService.ts
import api from '../../types/services/apiClient';
import { User, UserPreference, Notification, ActivityLog, ApiToken } from '../../types/domain/user';

export const userService = {
  // Obtener usuario actual
  getCurrentUser: (): Promise<{ data: User }> => 
    api.get('/api/users/profile/'),

  // Actualizar usuario
  updateUser: (id: number, userData: Partial<User>): Promise<{ data: User }> =>
    api.put(`/api/users/users/${id}/`, userData),

  // Obtener preferencias del usuario
  getUserPreferences: (): Promise<{ data: UserPreference[] }> =>
    api.get('/api/users/preferences/'),

  // Actualizar preferencias
  updatePreferences: (preferences: UserPreference[]): Promise<{ data: UserPreference[] }> =>
    api.put('/api/users/preferences/', { preferences }),

  // Obtener notificaciones
  getNotifications: (): Promise<{ data: Notification[] }> =>
    api.get('/api/users/notifications/'),

  // Marcar todas las notificaciones como leídas
  markAllNotificationsAsRead: (): Promise<void> =>
    api.post('/api/users/notifications/mark-all-read/'),

  // Obtener logs de actividad
  getActivityLogs: (): Promise<{ data: ActivityLog[] }> =>
    api.get('/api/users/activity-logs/'),

  // Obtener tokens API
  getApiTokens: (): Promise<{ data: ApiToken[] }> =>
    api.get('/api/users/api-tokens/'),

  // Generar nuevo token
  generateToken: (name: string): Promise<{ data: ApiToken }> =>
    api.post('/api/users/api-tokens/', { name }),

  // Revocar token
  revokeToken: (id: number): Promise<void> =>
    api.delete(`/api/users/api-tokens/${id}/`)
};