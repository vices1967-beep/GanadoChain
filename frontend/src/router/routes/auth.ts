import { lazy } from 'react';

// Componente temporal de registro
const Register = lazy(() => import('../../views/auth/Register').then(module => ({ default: module.default })));

export const authRoutes = [
  {
    path: '/login',
    component: lazy(() => import('../../views/auth/Login').then(module => ({ default: module.default }))),
    public: true,
  },
  {
    path: '/connect-wallet',
    component: lazy(() => import('../../views/auth/ConnectWallet').then(module => ({ default: module.default }))),
    public: true,
  },
  {
    path: '/register',
    component: Register,
    public: true,
  },
];