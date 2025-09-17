// contexts/auth/AuthContext.tsx
import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { Role } from '../../auth/permissions/constants';
import { Permission } from '../../auth/permissions/constants';
import { getUserPermissions } from '../../auth/permissions/permissions';
import { authService, User, LoginData } from '../../services/auth/authService';
import { JWT_ACCESS_TOKEN_KEY } from '../../utils/constants';
import LoadingSpinner from '../../components/ui/common/LoadingSpinner';

interface AuthContextType {
  user: User | null;
  roles: Role[];
  permissions: Permission[];
  isLoading: boolean;
  login: (credentials: LoginData) => Promise<void>;
  loginWithWallet: (walletAddress: string) => Promise<void>;
  logout: () => void;
  hasRole: (role: Role) => boolean;
  hasPermission: (permission: Permission) => boolean;
  mockLogin: (userRoles?: Role[]) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [roles, setRoles] = useState<Role[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem(JWT_ACCESS_TOKEN_KEY);
      
      if (token && authService.isAuthenticated()) {
        const userProfile = await authService.getProfile();
        setUser(userProfile);
        updateUserRolesAndPermissions(userProfile);
      }
    } catch (error) {
      console.error('Error checking authentication:', error);
      authService.logout();
      setUser(null);
      setRoles([]);
      setPermissions([]);
    } finally {
      setIsLoading(false);
    }
  };

  const updateUserRolesAndPermissions = (userData: User) => {
    const userRole = userData.role as Role;
    const userRoles = [userRole];
    setRoles(userRoles);
    setPermissions(getUserPermissions(userRole));
  };

  const login = async (credentials: LoginData) => {
    try {
      setIsLoading(true);
      // Eliminar la variable response no utilizada
      await authService.login(credentials);
      
      // Pequeña pausa para asegurar que el interceptor esté configurado
      await new Promise(resolve => setTimeout(resolve, 100));
      
      const userProfile = await authService.getProfile();
      setUser(userProfile);
      updateUserRolesAndPermissions(userProfile);
      
    } catch (error) {
      console.error('Login error:', error);
      authService.logout();
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const loginWithWallet = async (walletAddress: string) => {
    try {
      setIsLoading(true);
      await authService.connectWallet({ wallet_address: walletAddress });
      
      const userProfile = await authService.getProfile();
      setUser(userProfile);
      updateUserRolesAndPermissions(userProfile);
      
    } catch (error) {
      console.error('Wallet login error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    authService.logout();
    setUser(null);
    setRoles([]);
    setPermissions([]);
  };

  const mockLogin = (userRoles: Role[] = [Role.PRODUCER]) => {
    const mockUser: User = {
      id: 1,
      username: 'demo_user',
      email: 'demo@ganadochain.com',
      role: userRoles[0],
      wallet_address: '0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
      is_active: true,
      date_joined: new Date().toISOString(),
    };
    
    setUser(mockUser);
    setRoles(userRoles);
    
    // Combinar permisos de todos los roles
    const allPermissions = userRoles.flatMap(role => getUserPermissions(role));
    setPermissions(Array.from(new Set(allPermissions))); // Eliminar duplicados
  };

  const hasRole = (role: Role): boolean => {
    return roles.includes(role);
  };

  const hasPermission = (permission: Permission): boolean => {
    return permissions.includes(permission);
  };

  const value: AuthContextType = {
    user,
    roles,
    permissions,
    isLoading,
    login,
    loginWithWallet,
    logout,
    hasRole,
    hasPermission,
    mockLogin
  };

  return (
    <AuthContext.Provider value={value}>
      {isLoading ? <LoadingSpinner /> : children}
    </AuthContext.Provider>
  );
};