// App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import { AuthProvider, useAuth } from './contexts/auth/AuthContext';
import Login from './views/auth/Login';
import ConnectWallet from './views/auth/ConnectWallet';
import UserProfile from './components/User/UserProfile';
import Dashboard from './views/Dashboard';
import DashboardLayout from './components/ui/layout/DashboardLayout';
import LoadingSpinner from './components/ui/common/LoadingSpinner';
import './assets/styles/global.scss';
import { store } from './stores/store';

// Importar vistas de Cattle
import AnimalsView from './features/cattle/views/AnimalsView';
import BatchesView from './features/cattle/views/BatchesView';
import CertificationsView from './features/cattle/views/CertificationsView';
import HealthView from './features/cattle/views/HealthView';
import CattleDashboard from './features/cattle/views/DashboardView';

const AuthWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isLoading } = useAuth();
  
  if (isLoading) {
    return <LoadingSpinner />;
  }
  
  return <>{children}</>;
};

const AuthOnlyGuard: React.FC<{ children: React.ReactElement }> = ({ children }) => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return user ? children : <Navigate to="/login" replace />;
};

// Layout para páginas que necesitan sidebar/header
const WithAppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <DashboardLayout>{children}</DashboardLayout>;
};

const App: React.FC = () => {
  return (
    <Provider store={store}>
      <AuthProvider>
        <Router>
          <AuthWrapper>
            <Routes>
              {/* Rutas públicas sin layout */}
              <Route path="/login" element={<Login />} />
              <Route path="/connect-wallet" element={<ConnectWallet />} />
              
              {/* Dashboard principal */}
              <Route
                path="/dashboard"
                element={
                  <AuthOnlyGuard>
                    <Dashboard />
                  </AuthOnlyGuard>
                }
              />

              {/* Rutas de Cattle con layout */}
              <Route
                path="/animals"
                element={
                  <AuthOnlyGuard>
                    <WithAppLayout>
                      <AnimalsView />
                    </WithAppLayout>
                  </AuthOnlyGuard>
                }
              />
              <Route
                path="/batches"
                element={
                  <AuthOnlyGuard>
                    <WithAppLayout>
                      <BatchesView />
                    </WithAppLayout>
                  </AuthOnlyGuard>
                }
              />
              <Route
                path="/certifications"
                element={
                  <AuthOnlyGuard>
                    <WithAppLayout>
                      <CertificationsView />
                    </WithAppLayout>
                  </AuthOnlyGuard>
                }
              />
              <Route
                path="/health"
                element={
                  <AuthOnlyGuard>
                    <WithAppLayout>
                      <HealthView />
                    </WithAppLayout>
                  </AuthOnlyGuard>
                }
              />
              <Route
                path="/cattle-dashboard"
                element={
                  <AuthOnlyGuard>
                    <WithAppLayout>
                      <CattleDashboard />
                    </WithAppLayout>
                  </AuthOnlyGuard>
                }
              />
              
              {/* UserProfile */}
              <Route
                path="/profile"
                element={
                  <AuthOnlyGuard>
                    <WithAppLayout>
                      <UserProfile />
                    </WithAppLayout>
                  </AuthOnlyGuard>
                }
              />
              
              {/* Redirección por defecto al dashboard */}
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              
              {/* Ruta para páginas no encontradas */}
              <Route path="*" element={
                <WithAppLayout>
                  <div>Página no encontrada</div>
                </WithAppLayout>
              } />
            </Routes>
          </AuthWrapper>
        </Router>
      </AuthProvider>
    </Provider>
  );
};

export default App;