// App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux'; // Importar Provider de Redux
import { AuthProvider, useAuth } from './contexts/auth/AuthContext';
import Login from './views/auth/Login';
import ConnectWallet from './views/auth/ConnectWallet';
import UserProfile from './components/User/UserProfile';
import Dashboard from './views/Dashboard';
import DashboardLayout from './components/ui/layout/DashboardLayout';
import LoadingSpinner from './components/ui/common/LoadingSpinner';
import './assets/styles/global.scss';
import { store } from './stores/store'; // Importar el store de Redux

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

// Layout para páginas que necesitan sidebar/header (como UserProfile)
const WithAppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <DashboardLayout>{children}</DashboardLayout>;
};

const App: React.FC = () => {
  return (
    <Provider store={store}> {/* Envolver toda la app con Redux Provider */}
      <AuthProvider>
        <Router>
          <AuthWrapper>
            <Routes>
              {/* Rutas públicas sin layout */}
              <Route path="/login" element={<Login />} />
              <Route path="/connect-wallet" element={<ConnectWallet />} />
              
              {/* Dashboard - NO usar layout porque ya lo tiene internamente */}
              <Route
                path="/dashboard"
                element={
                  <AuthOnlyGuard>
                    <Dashboard />
                  </AuthOnlyGuard>
                }
              />
              
              {/* UserProfile - SÍ necesita layout */}
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