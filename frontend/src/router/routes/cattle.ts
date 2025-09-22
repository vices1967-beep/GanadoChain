// src/router/routes/cattle.ts
import { lazy } from 'react';

export const cattleRoutes = [
  {
    path: '/animals',
    component: lazy(() => import('../../features/cattle/views/AnimalsView')),
    roles: ['producer', 'admin', 'veterinarian'],
    title: 'Animales'
  },
  {
    path: '/batches',
    component: lazy(() => import('../../features/cattle/views/BatchesView')),
    roles: ['producer', 'admin'],
    title: 'Lotes'
  },
  {
    path: '/certifications',
    component: lazy(() => import('../../features/cattle/views/CertificationsView')),
    roles: ['producer', 'admin', 'auditor'],
    title: 'Certificaciones'
  },
  {
    path: '/health',
    component: lazy(() => import('../../features/cattle/views/HealthView')),
    roles: ['veterinarian', 'admin', 'producer'],
    title: 'Salud'
  },
  {
    path: '/cattle-dashboard',
    component: lazy(() => import('../../features/cattle/views/DashboardView')),
    roles: ['producer', 'admin', 'veterinarian'],
    title: 'Dashboard Ganado'
  }
];