import React from 'react';
import { useAuth } from '../../contexts/auth/AuthContext';
import { Role } from '../permissions/roles';

interface RoleGuardProps {
  requiredRole: Role;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export const RoleGuard: React.FC<RoleGuardProps> = ({
  requiredRole,
  children,
  fallback = null
}) => {
  const { hasRole } = useAuth();

  if (hasRole(requiredRole)) {
    return <>{children}</>;
  }

  return <>{fallback}</>;
};

// Hook para uso en componentes
export const useRoleGuard = (requiredRole: Role): boolean => {
  const { hasRole } = useAuth();
  return hasRole(requiredRole);
};