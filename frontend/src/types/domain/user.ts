// src/types/domain/user.ts
export interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  profile_image?: string;
  date_joined: string;
  last_login: string;
  role: string;
  wallet_address?: string;
  is_active: boolean;
}

export interface UserPreference {
  key: string;
  value: any;
}

export interface Notification {
  id: number;
  message: string;
  timestamp: string;
  read: boolean;
  type?: string;
  metadata?: Record<string, any>;
}

export interface ActivityLog {
  id: number;
  action: string;
  timestamp: string;
  ip_address?: string;
  user_agent?: string;
  metadata?: Record<string, any>;
}

export interface ApiToken {
  id: number;
  name: string;
  token?: string;
  last_used?: string;
  created: string;
  expires?: string;
  is_active: boolean;
}