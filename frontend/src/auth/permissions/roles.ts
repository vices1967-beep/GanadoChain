// src/auth/permissions/roles.ts
import { Role, Permission } from './constants';

export { Role }; // ← Añadir esta línea para exportar Role

export const ROLE_PERMISSIONS: Record<Role, Permission[]> = {
  [Role.ADMIN]: [
    Permission.ANIMAL_VIEW,
    Permission.ANIMAL_CREATE,
    Permission.ANIMAL_EDIT,
    Permission.ANIMAL_DELETE,
    Permission.BATCH_VIEW,
    Permission.BATCH_CREATE,
    Permission.BATCH_EDIT,
    Permission.BATCH_DELETE,
    Permission.CERTIFICATION_VIEW,
    Permission.CERTIFICATION_CREATE,
    Permission.CERTIFICATION_EDIT,
    Permission.CERTIFICATION_DELETE,
    Permission.USER_VIEW,
    Permission.USER_CREATE,
    Permission.USER_EDIT,
    Permission.USER_DELETE,
    Permission.ADMIN_ACCESS,
    Permission.SYSTEM_CONFIG,
    Permission.IOT_VIEW,
    Permission.IOT_MANAGE,
    Permission.MARKET_VIEW,
    Permission.MARKET_TRADE,
    Permission.BLOCKCHAIN_INTERACT,
    Permission.NFT_MINT,
  ],
  [Role.PRODUCER]: [
    Permission.ANIMAL_VIEW,
    Permission.ANIMAL_CREATE,
    Permission.ANIMAL_EDIT,
    Permission.BATCH_VIEW,
    Permission.BATCH_CREATE,
    Permission.BATCH_EDIT,
    Permission.CERTIFICATION_VIEW,
    Permission.CERTIFICATION_CREATE,
    Permission.IOT_VIEW,
    Permission.MARKET_VIEW,
    Permission.MARKET_TRADE,
    Permission.BLOCKCHAIN_INTERACT,
  ],
  [Role.VETERINARIAN]: [
    Permission.ANIMAL_VIEW,
    Permission.ANIMAL_EDIT,
    Permission.CERTIFICATION_VIEW,
    Permission.CERTIFICATION_CREATE,
    Permission.IOT_VIEW,
  ],
  [Role.CONSUMER]: [
    Permission.ANIMAL_VIEW,
    Permission.CERTIFICATION_VIEW,
    Permission.MARKET_VIEW,
  ],
  [Role.AUDITOR]: [
    Permission.ANIMAL_VIEW,
    Permission.BATCH_VIEW,
    Permission.CERTIFICATION_VIEW,
    Permission.USER_VIEW,
  ],
};

export const ROLE_HIERARCHY: Record<Role, number> = {
  [Role.ADMIN]: 100,
  [Role.AUDITOR]: 80,
  [Role.VETERINARIAN]: 60,
  [Role.PRODUCER]: 40,
  [Role.CONSUMER]: 20,
};

export const canElevate = (currentRole: Role, targetRole: Role): boolean => {
  return ROLE_HIERARCHY[currentRole] >= ROLE_HIERARCHY[targetRole];
};