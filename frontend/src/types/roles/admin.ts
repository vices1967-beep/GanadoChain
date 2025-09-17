import { BaseUser } from './common';

export interface AdminUser extends BaseUser {
  role: 'admin';
  permissions: string[];
  canManageSystem: boolean;
}