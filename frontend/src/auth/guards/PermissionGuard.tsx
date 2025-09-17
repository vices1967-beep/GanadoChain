// src/auth/guards/PermissionGuard.tsx
import React from 'react';
import { useAuth } from '../../contexts/auth/AuthContext';
import { Permission } from '../permissions/constants';
import { checkUserPermission } from '../permissions/permissions';
import LoadingSpinner from '../../components/ui/common/LoadingSpinner';

interface PermissionGuardProps {
  children: React.ReactNode;
  requiredPermission: Permission;
  fallback?: React.ReactNode;
}

const PermissionGuard: React.FC<PermissionGuardProps> = ({
  children,
  requiredPermission,
  fallback = null,
}) => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (!user) {
    return <>{fallback}</>;
  }

  const hasPermission = checkUserPermission(user.role as any, requiredPermission);

  if (!hasPermission) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
};

export default PermissionGuard;