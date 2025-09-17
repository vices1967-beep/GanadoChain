// src/auth/permissions/permissions.ts
import { ROLE_PERMISSIONS, Role } from './roles';
import { Permission } from './constants';

export const hasRolePermission = (role: Role, permission: Permission): boolean => {
  return ROLE_PERMISSIONS[role]?.includes(permission) || false;
};

export const checkUserPermission = (userRole: Role, requiredPermission: Permission): boolean => {
  return hasRolePermission(userRole, requiredPermission);
};

export const hasAnyPermission = (role: Role, permissions: Permission[]): boolean => {
  return permissions.some(permission => hasRolePermission(role, permission));
};

export const hasAllPermissions = (role: Role, permissions: Permission[]): boolean => {
  return permissions.every(permission => hasRolePermission(role, permission));
};

// Añadir esta función si se necesita en AuthContext
export const getUserPermissions = (role: Role): Permission[] => {
  return ROLE_PERMISSIONS[role] || [];
};