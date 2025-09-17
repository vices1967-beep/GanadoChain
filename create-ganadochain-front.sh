#!/bin/bash

# create-ganadochain-front.sh
# Crea la estructura completa del frontend de GanadoChain desde cero

PROJECT_NAME="front"
echo "🚀 Creando proyecto GanadoChain Frontend en '$PROJECT_NAME'..."

# 1. Crear directorio principal
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME" || exit 1

# 2. Inicializar npm
npm init -y

# 3. Instalar dependencias esenciales
npm install next react react-dom typescript ts-node @types/react @types/node
npm install tailwindcss postcss autoprefixer
npm install zod
npm install zustand axios
npm install --save-dev @types/react-dom

# 4. Generar configuración de Tailwind
npx tailwindcss init -p

# 5. Crear estructura de carpetas
mkdir -p app
mkdir -p components/layout
mkdir -p components/ui
mkdir -p components/icons
mkdir -p api/core
mkdir -p api/cattle
mkdir -p api/analytics
mkdir -p api/users
mkdir -p api/blockchain
mkdir -p zod/schemas
mkdir -p store/zustand
mkdir -p lib
mkdir -p public/images
mkdir -p styles

# 6. Crear archivos clave

# app/layout.tsx
cat > app/layout.tsx << 'EOF'
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "GanadoChain - Rastreo Blockchain de Ganado",
  description: "Sistema integral de gestión de ganado con blockchain, IoT y certificaciones.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body className="min-h-screen bg-gray-50 font-sans">
        {children}
      </body>
    </html>
  );
}
EOF

# app/dashboard/layout.tsx
cat > app/dashboard/layout.tsx << 'EOF'
import Header from "@/components/layout/Header";
import Sidebar from "@/components/layout/Sidebar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Header */}
        <Header />

        {/* Content */}
        <main className="flex-1 overflow-y-auto p-6 bg-gray-50">
          {children}
        </main>
      </div>
    </div>
  );
}
EOF

# app/dashboard/page.tsx
cat > app/dashboard/page.tsx << 'EOF'
import WidgetGrid from "@/components/layout/WidgetGrid";

export default function DashboardPage() {
  return <WidgetGrid />;
}
EOF

# app/auth/page.tsx
cat > app/auth/page.tsx << 'EOF'
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/zustand/authStore';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();
  const login = useAuthStore((state) => state.login);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) throw new Error('Credenciales inválidas');

      const data = await res.json();
      localStorage.setItem('token', data.token);
      login(data.token, data.user);
      router.push('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h1 className="text-2xl font-bold text-center mb-6">Iniciar Sesión</h1>
        {error && <p className="text-red-500 mb-4">{error}</p>}
        <form onSubmit={handleSubmit}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded mb-4 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            required
          />
          <input
            type="password"
            placeholder="Contraseña"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded mb-6 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            required
          />
          <button
            type="submit"
            className="w-full bg-indigo-600 text-white py-3 rounded font-medium hover:bg-indigo-700 transition"
          >
            Ingresar
          </button>
        </form>
      </div>
    </div>
  );
}
EOF

# components/layout/Header.tsx
cat > components/layout/Header.tsx << 'EOF'
'use client';

import { useAuthStore } from '@/store/zustand/authStore';
import Link from 'next/link';

export default function Header() {
  const { user, logout } = useAuthStore();

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4 flex items-center justify-between">
      <h1 className="text-xl font-bold text-gray-900">Dashboard</h1>

      <div className="flex items-center space-x-4">
        <button className="relative p-2 text-gray-600 hover:text-gray-900 transition">
          <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 17h5l-5 5v-5zM10.5 19.5L6 15m0 0l4.5-4.5M6 15l4.5 4.5" />
          </svg>
          <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></span>
        </button>

        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center text-xs font-medium">
            {user?.name?.[0] || 'U'}
          </div>
          <span className="hidden md:block text-sm font-medium text-gray-700">{user?.name}</span>
        </div>
      </div>
    </header>
  );
}
EOF

# components/layout/Sidebar.tsx
cat > components/layout/Sidebar.tsx << 'EOF'
'use client';

import { useAuthStore } from '@/store/zustand/authStore';
import Link from 'next/link';
import { ChartBarIcon, AnimalIcon, ShieldIcon } from '@/components/icons';

const Sidebar = () => {
  const { role } = useAuthStore();

  const menuItems = [
    { name: 'Dashboard', href: '/dashboard', icon: ChartBarIcon },
    { name: 'Ganado', href: '/cattle', icon: AnimalIcon },
    { name: 'Analytics', href: '/analytics', icon: ChartBarIcon },
    { name: 'Blockchain', href: '/blockchain', icon: ShieldIcon },
  ];

  const adminProducerMenu = [
    { name: 'IoT', href: '/iot', icon: AnimalIcon },
    { name: 'Mercado', href: '/market', icon: ChartBarIcon },
    { name: 'Recompensas', href: '/rewards', icon: ShieldIcon },
    { name: 'Informes', href: '/reports', icon: ChartBarIcon },
  ];

  const consumerMenu = [
    { name: 'Buscar Ganado', href: '/consumer', icon: AnimalIcon },
    { name: 'Certificaciones', href: '/consumer/certification', icon: ShieldIcon },
  ];

  const allItems = role === 'consumer'
    ? [...menuItems, ...consumerMenu]
    : [...menuItems, ...(role === 'admin' || role === 'producer' ? adminProducerMenu : [])];

  return (
    <aside className="w-64 bg-indigo-900 text-white flex flex-col shadow-lg">
      <div className="p-4 flex items-center border-b border-indigo-700">
        <div className="w-8 h-8 bg-gradient-to-r from-green-400 to-blue-500 rounded-full flex items-center justify-center text-sm font-bold">
          GC
        </div>
        <span className="ml-3 font-semibold">GanadoChain</span>
      </div>

      <nav className="flex-1 px-2 py-4 space-y-1">
        {allItems.map((item) => (
          <Link
            key={item.name}
            href={item.href}
            className={`flex items-center px-3 py-3 rounded-lg transition-colors group ${
              window.location.pathname === item.href
                ? 'bg-indigo-700 text-white shadow-md'
                : 'text-indigo-200 hover:bg-indigo-800 hover:text-white'
            }`}
          >
            <item.icon className="w-5 h-5 flex-shrink-0" />
            <span className="ml-3 truncate">{item.name}</span>
          </Link>
        ))}
      </nav>

      <div className="p-4 border-t border-indigo-700">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center text-xs font-medium">
            {role?.[0]?.toUpperCase() || 'U'}
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium">Usuario</p>
            <p className="text-xs text-indigo-300 capitalize">{role}</p>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
EOF

# components/layout/WidgetGrid.tsx
cat > components/layout/WidgetGrid.tsx << 'EOF'
'use client';

import { useEffect, useState } from 'react';
import { useDashboardStore } from '@/store/zustand/dashboardStore';
import { useAuthStore } from '@/store/zustand/authStore';
import { getMetrics } from '@/api/core/metrics';
import { getAnimalStats } from '@/api/cattle/stats';
import { getHealthTrends } from '@/api/analytics/health-trends';
import { metricSchema, animalStatsSchema, healthTrendSchema } from '@/zod/schemas';
import Card from '@/components/ui/Card';

export default function WidgetGrid() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { role } = useAuthStore();
  const { setMetrics, setAnimalStats, setHealthTrends } = useDashboardStore();

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [metricsRes, statsRes, trendsRes] = await Promise.all([
          getMetrics(),
          getAnimalStats(),
          getHealthTrends(),
        ]);

        const validatedMetrics = metricSchema.parse(metricsRes);
        const validatedStats = animalStatsSchema.parse(statsRes);
        const validatedTrends = healthTrendSchema.parse(trendsRes);

        setMetrics(validatedMetrics);
        setAnimalStats(validatedStats);
        setHealthTrends(validatedTrends);

      } catch (err) {
        if (err instanceof Error) setError(err.message);
        else setError('Error desconocido al cargar datos');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [role]);

  if (loading) return <div className="flex items-center justify-center h-64">Cargando...</div>;
  if (error) return <div className="text-red-500 p-4">{error}</div>;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6 mb-8">
      <Card title="Animales Totales" value={useDashboardStore.getState().animalStats.total} icon="🐄" color="bg-green-500" />
      <Card title="Salud Promedio" value={`${useDashboardStore.getState().healthTrends.average}%`} icon="❤️" color="bg-blue-500" />
      <Card title="Eventos Blockchain" value={useDashboardStore.getState().metrics.events} icon="🔗" color="bg-purple-500" />

      {(useAuthStore.getState().role === 'admin' || useAuthStore.getState().role === 'producer') && (
        <>
          <Card title="Dispositivos IoT" value={useDashboardStore.getState().metrics.iotDevices} icon="📡" color="bg-orange-500" />
          <Card title="Valor Mercado" value={`$${useDashboardStore.getState().animalStats.marketValue.toLocaleString()}`} icon="💰" color="bg-yellow-500" />
        </>
      )}
    </div>
  );
}
EOF

# components/ui/Card.tsx
cat > components/ui/Card.tsx << 'EOF'
'use client';

interface CardProps {
  title: string;
  value: string | number;
  icon: string;
  color: string;
}

export default function Card({ title, value, icon, color }: CardProps) {
  return (
    <div className={`bg-white rounded-xl shadow-md p-6 flex flex-col items-center justify-center text-center hover:shadow-lg transition-shadow ${color}`}>
      <div className="text-4xl mb-2">{icon}</div>
      <h3 className="text-gray-600 text-sm font-medium mb-1">{title}</h3>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
    </div>
  );
}
EOF

# components/icons/ChartBarIcon.tsx
mkdir -p components/icons
cat > components/icons/ChartBarIcon.tsx << 'EOF'
export function ChartBarIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
    </svg>
  );
}
EOF

# components/icons/AnimalIcon.tsx
cat > components/icons/AnimalIcon.tsx << 'EOF'
export function AnimalIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
    </svg>
  );
}
EOF

# components/icons/ShieldIcon.tsx
cat > components/icons/ShieldIcon.tsx << 'EOF'
export function ShieldIcon({ className }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
    </svg>
  );
}
EOF

# zod/schemas/metricSchema.ts
mkdir -p zod/schemas
cat > zod/schemas/metricSchema.ts << 'EOF'
import { z } from 'zod';

export const metricSchema = z.object({
  events: z.number().int().positive(),
  iotDevices: z.number().int().nonnegative(),
  systemHealth: z.enum(['healthy', 'warning', 'critical']),
});

export type MetricType = z.infer<typeof metricSchema>;
EOF

# zod/schemas/animalStatsSchema.ts
cat > zod/schemas/animalStatsSchema.ts << 'EOF'
import { z } from 'zod';

export const animalStatsSchema = z.object({
  total: z.number().int().nonnegative(),
  healthy: z.number().int().nonnegative(),
  marketValue: z.number().positive(),
});

export type AnimalStatsType = z.infer<typeof animalStatsSchema>;
EOF

# zod/schemas/healthTrendSchema.ts
cat > zod/schemas/healthTrendSchema.ts << 'EOF'
import { z } from 'zod';

export const healthTrendSchema = z.object({
  average: z.number().min(0).max(100),
  trend: z.enum(['up', 'down', 'stable']),
});

export type HealthTrendType = z.infer<typeof healthTrendSchema>;
EOF

# store/zustand/authStore.ts
mkdir -p store/zustand
cat > store/zustand/authStore.ts << 'EOF'
import { create } from 'zustand';

interface AuthState {
  user: {
    id: string;
    name: string;
    email: string;
    role: 'admin' | 'producer' | 'consumer';
  } | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (token: string, userData: any) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,

  login: (token, userData) =>
    set((state) => ({
      token,
      user: {
        id: userData.id,
        name: userData.name,
        email: userData.email,
        role: userData.role,
      },
      isAuthenticated: true,
    })),

  logout: () =>
    set({
      user: null,
      token: null,
      isAuthenticated: false,
    }),
}));
EOF

# store/zustand/dashboardStore.ts
cat > store/zustand/dashboardStore.ts << 'EOF'
import { create } from 'zustand';

interface DashboardState {
  metrics: {
    events: number;
    iotDevices: number;
    systemHealth: 'healthy' | 'warning' | 'critical';
  };
  animalStats: {
    total: number;
    healthy: number;
    marketValue: number;
  };
  healthTrends: {
    average: number;
    trend: 'up' | 'down' | 'stable';
  };
  setMetrics: (data: typeof dashboardStore.initialState.metrics) => void;
  setAnimalStats: (data: typeof dashboardStore.initialState.animalStats) => void;
  setHealthTrends: (data: typeof dashboardStore.initialState.healthTrends) => void;
}

const initialState = {
  metrics: {
    events: 0,
    iotDevices: 0,
    systemHealth: 'healthy',
  },
  animalStats: {
    total: 0,
    healthy: 0,
    marketValue: 0,
  },
  healthTrends: {
    average: 0,
    trend: 'stable',
  },
};

export const useDashboardStore = create<DashboardState>((set) => ({
  ...initialState,

  setMetrics: (metrics) => set({ metrics }),
  setAnimalStats: (animalStats) => set({ animalStats }),
  setHealthTrends: (healthTrends) => set({ healthTrends }),
}));
EOF

# lib/apiClient.ts
mkdir -p lib
cat > lib/apiClient.ts << 'EOF'
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000/api',
  timeout: 10000,
});

// Interceptor: Agregar token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = \`Bearer \${token}\`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor: Manejar errores 401
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/auth';
    }
    return Promise.reject(error);
  }
);

export { apiClient };
EOF

# api/core/metrics.ts
cat > api/core/metrics.ts << 'EOF'
import { apiClient } from '@/lib/apiClient';
import { metricSchema } from '@/zod/schemas';

export const getMetrics = async () => {
  const response = await apiClient.get('/api/core/metrics');
  return metricSchema.parse(response.data);
};
EOF

# api/cattle/stats.ts
cat > api/cattle/stats.ts << 'EOF'
import { apiClient } from '@/lib/apiClient';
import { animalStatsSchema } from '@/zod/schemas';

export const getAnimalStats = async () => {
  const response = await apiClient.get('/api/cattle/stats');
  return animalStatsSchema.parse(response.data);
};
EOF

# api/analytics/health-trends.ts
cat > api/analytics/health-trends.ts << 'EOF'
import { apiClient } from '@/lib/apiClient';
import { healthTrendSchema } from '@/zod/schemas';

export const getHealthTrends = async () => {
  const response = await apiClient.get('/api/analytics/health-trends');
  return healthTrendSchema.parse(response.data);
};
EOF

# tailwind.config.js
cat > tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,jsx,ts,tsx}",
    "./components/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
EOF

# jsconfig.json (para mejor autocompletado en VSCode)
cat > jsconfig.json << 'EOF'
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"]
}
EOF

# next.config.mjs
cat > next.config.mjs << 'EOF'
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
}

export default nextConfig;
EOF

# tsconfig.json
cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ]
  },
  "include": [
    "next-env.d.ts",
    "**/*.ts",
    "**/*.tsx"
  ],
  "exclude": ["node_modules"]
}
EOF

# package.json (añadir scripts)
npm pkg set scripts.dev="next dev" scripts.build="next build" scripts.start="next start" scripts.export="next export"

# .gitignore
cat > .gitignore << 'EOF'
node_modules/
.next/
out/
dist/
*.log
npm-debug.log*
.env.local
EOF

# styles/globals.css
cat > styles/globals.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-gray-50;
  }
}
EOF

# Final message
echo ""
echo "🎉 ¡PROYECTO GANADOCHAIN FRONTEND CREADO EXITOSAMENTE!"
echo ""
echo "📁 Estructura creada en: $PROJECT_NAME/"
echo ""
echo "📝 Pasos siguientes:"
echo "1. cd $PROJECT_NAME"
echo "2. npm run dev"
echo "3. Abre http://localhost:3000/dashboard"
echo ""
echo "💡 Recuerda: El backend debe estar corriendo en http://localhost:3000/api para que las APIs funcionen."
echo ""
echo "✅ Todo está listo: Zod, Zustand, Tailwind, Next.js App Router, estructura modular."
