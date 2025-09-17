import React from 'react';
import { useAuth } from '../../contexts/auth/AuthContext';
import { Role } from '../permissions/roles';

interface RoleBasedRendererProps {
  requiredRole: Role;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export const RoleBasedRenderer: React.FC<RoleBasedRendererProps> = ({
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