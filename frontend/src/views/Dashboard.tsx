// src/views/Dashboard.tsx
import React from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  Chip,
  Stack
} from '@mui/material';
import {
  Pets as AnimalsIcon,
  Groups as BatchesIcon,
  Assignment as CertificationsIcon,
  ShowChart as AnalyticsIcon,
  Add as AddIcon,
  TrendingUp as TrendingUpIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/auth/AuthContext';
import DashboardLayout from '../components/ui/layout/DashboardLayout';
import '../assets/styles/global.scss';

const StatCard: React.FC<{
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color?: 'primary' | 'secondary' | 'success' | 'info';
  trend?: string;
}> = ({ title, value, icon, color = 'primary', trend }) => (
  <Card className="stat-card">
    <CardContent className="stat-card-content">
      <Box className="stat-card-inner">
        <Box className="stat-card-text">
          <Typography variant="overline" className="stat-card-title">
            {title}
          </Typography>
          <Typography variant="h4" className="stat-card-value">
            {value}
          </Typography>
          {trend && (
            <Chip
              icon={<TrendingUpIcon />}
              label={trend}
              size="small"
              className={`stat-card-trend trend-${color}`}
            />
          )}
        </Box>
        <Box className={`stat-card-icon icon-${color}`}>
          {icon}
        </Box>
      </Box>
    </CardContent>
  </Card>
);

const QuickAction: React.FC<{
  title: string;
  description: string;
  icon: React.ReactNode;
  buttonText: string;
  onClick: () => void;
  color?: 'primary' | 'secondary' | 'success' | 'info';
}> = ({ title, description, icon, buttonText, onClick, color = 'primary' }) => (
  <Paper className="quick-action-card">
    <Box className="quick-action-header">
      <Box className={`quick-action-icon icon-${color}`}>
        {icon}
      </Box>
      <Typography variant="h6" className="quick-action-title">
        {title}
      </Typography>
    </Box>
    <Typography variant="body2" className="quick-action-description">
      {description}
    </Typography>
    <Button
      variant="contained"
      startIcon={<AddIcon />}
      onClick={onClick}
      className={`quick-action-button button-${color}`}
      fullWidth
    >
      {buttonText}
    </Button>
  </Paper>
);

const Dashboard: React.FC = () => {
  const { user } = useAuth();

  const quickActions = [
    {
      title: 'Registrar Animal',
      description: 'Agregar nuevo animal al sistema con todos sus datos',
      icon: <AnimalsIcon />,
      buttonText: 'Nuevo Animal',
      onClick: () => console.log('Registrar animal'),
      color: 'primary' as const
    },
    {
      title: 'Crear Lote',
      description: 'Organizar animales en lotes para mejor gestión',
      icon: <BatchesIcon />,
      buttonText: 'Crear Lote',
      onClick: () => console.log('Crear lote'),
      color: 'secondary' as const
    },
    {
      title: 'Certificar',
      description: 'Gestionar certificaciones de calidad y origen',
      icon: <CertificationsIcon />,
      buttonText: 'Iniciar Certificación',
      onClick: () => console.log('Certificar'),
      color: 'success' as const
    }
  ];

  return (
    <DashboardLayout>
      <Box className="dashboard-content">
        {/* Welcome Banner */}
        <Paper className="welcome-banner">
          <Typography variant="h4" className="welcome-title">
            🐄 Bienvenido a GanadoChain
          </Typography>
          <Typography variant="body1" className="welcome-subtitle">
            Sistema de trazabilidad blockchain para ganado. 
            Gestiona tus animales, lotes, certificaciones y más.
          </Typography>
          <Stack direction="row" spacing={1} className="welcome-chips">
            <Chip label={`Usuario: ${user?.username}`} className="user-chip" />
            <Chip label={`Rol: ${user?.role}`} className="role-chip" />
            {user?.wallet_address && (
              <Chip 
                label={`Wallet: ${user.wallet_address.slice(0, 8)}...${user.wallet_address.slice(-6)}`} 
                className="wallet-chip"
              />
            )}
          </Stack>
        </Paper>

        {/* Statistics Grid - Sintaxis corregida para MUI v7.3 */}
        <Grid container spacing={3} className="stats-grid">
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <StatCard
              title="Total Animales"
              value="142"
              icon={<AnimalsIcon />}
              color="primary"
              trend="+12%"
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <StatCard
              title="Lotes Activos"
              value="8"
              icon={<BatchesIcon />}
              color="secondary"
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <StatCard
              title="Certificaciones"
              value="24"
              icon={<CertificationsIcon />}
              color="success"
              trend="+5%"
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <StatCard
              title="Salud Promedio"
              value="92%"
              icon={<AnalyticsIcon />}
              color="info"
            />
          </Grid>
        </Grid>

        {/* Quick Actions */}
        <Typography variant="h5" className="section-title">
          Acciones Rápidas
        </Typography>
        <Grid container spacing={3} className="quick-actions-grid">
          {quickActions.map((action, index) => (
            <Grid size={{ xs: 12, md: 4 }} key={index}>
              <QuickAction {...action} />
            </Grid>
          ))}
        </Grid>

        {/* Recent Activity */}
        <Paper className="recent-activity">
          <Typography variant="h6" className="activity-title">
            Actividad Reciente
          </Typography>
          <Typography variant="body2" className="activity-placeholder">
            Aquí se mostrará el historial de actividades recientes del sistema...
          </Typography>
        </Paper>
      </Box>
    </DashboardLayout>
  );
};

export default Dashboard;