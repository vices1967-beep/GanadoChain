// src/views/Dashboard.tsx
import React, { useEffect, useState } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  Chip,
  Stack,
  CircularProgress,
  Alert
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
import { useCattle } from '../hooks/cattle/useCattle';
import DashboardLayout from '../components/ui/layout/DashboardLayout';
import { useNavigate } from 'react-router-dom';
import { Animal, Batch } from '../types/domain/cattle';
import '../assets/styles/global.scss';

const StatCard: React.FC<{
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color?: 'primary' | 'secondary' | 'success' | 'info';
  trend?: string;
  loading?: boolean;
}> = ({ title, value, icon, color = 'primary', trend, loading = false }) => (
  <Card className="stat-card">
    <CardContent className="stat-card-content">
      <Box className="stat-card-inner">
        <Box className="stat-card-text">
          <Typography variant="overline" className="stat-card-title">
            {title}
          </Typography>
          {loading ? (
            <CircularProgress size={32} className="stat-card-loading" />
          ) : (
            <Typography variant="h4" className="stat-card-value">
              {value}
            </Typography>
          )}
          {trend && !loading && (
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
  const { 
    getAnimals, 
    getBatches, 
    getAnimalCertifications, 
    getStats 
  } = useCattle();
  const navigate = useNavigate();
  
  const [cattleStats, setCattleStats] = useState({
    totalAnimals: 0,
    totalBatches: 0,
    totalCertifications: 0,
    healthStatus: 'Cargando...'
  });
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    loadCattleData();
  }, []);

  const loadCattleData = async () => {
    try {
      setIsLoading(true);
      setLoadError(null);
      
      console.log('🔍 Cargando datos de cattle...');
      
      // Cargar datos básicos primero con mejor manejo de errores
      let animalsData: Animal[] = [];
      let batchesData: Batch[] = [];
      
      try {
        const [animalsResult, batchesResult] = await Promise.all([
          getAnimals(),
          getBatches()
        ]);
        
        console.log('🔍 Resultado de getAnimals():', animalsResult);
        console.log('🔍 Tipo de animalsResult:', typeof animalsResult);
        console.log('🔍 Es array?', Array.isArray(animalsResult));
        
        console.log('🔍 Resultado de getBatches():', batchesResult);
        console.log('🔍 Tipo de batchesResult:', typeof batchesResult);
        console.log('🔍 Es array?', Array.isArray(batchesResult));
        
        animalsData = Array.isArray(animalsResult) ? animalsResult : [];
        batchesData = Array.isArray(batchesResult) ? batchesResult : [];
      } catch (error) {
        console.warn('⚠️ Error loading basic data:', error);
        // Si falla, intentar cargar por separado
        try {
          const animals = await getAnimals();
          animalsData = Array.isArray(animals) ? animals : [];
        } catch (e) {
          animalsData = [];
        }
        try {
          const batches = await getBatches();
          batchesData = Array.isArray(batches) ? batches : [];
        } catch (e) {
          batchesData = [];
        }
      }

      console.log('✅ Datos básicos cargados:', {
        animales: animalsData.length,
        lotes: batchesData.length
      });

      // Cargar estadísticas
      let statsData = null;
      try {
        statsData = await getStats();
        console.log('📊 Estadísticas cargadas:', statsData);
      } catch (statsError) {
        console.warn('⚠️ Error loading stats:', statsError);
      }

      // Calcular certificaciones - Estrategia optimizada
      let certificationCount = 0;
      if (animalsData && animalsData.length > 0) {
        try {
          // Estrategia: Muestreo inteligente (más rápido)
          const sampleSize = Math.min(3, animalsData.length);
          const sampleAnimals = animalsData.slice(0, sampleSize);
          
          const sampleCertPromises = sampleAnimals.map(animal =>
            getAnimalCertifications(animal.id).catch(() => [])
          );
          
          const sampleCerts = await Promise.all(sampleCertPromises);
          const avgCertsPerAnimal = sampleCerts.reduce((sum, certs) => sum + (certs?.length || 0), 0) / sampleSize;
          certificationCount = Math.round(avgCertsPerAnimal * animalsData.length);
          
          console.log('📝 Certificaciones estimadas:', certificationCount);

        } catch (certError) {
          console.warn('⚠️ Error estimating certifications:', certError);
          certificationCount = Math.round(animalsData.length * 0.3);
        }
      }

      setCattleStats({
        totalAnimals: animalsData?.length || 0,
        totalBatches: batchesData?.length || 0,
        totalCertifications: certificationCount,
        healthStatus: statsData?.animals_by_health_status?.HEALTHY 
          ? `${Math.round((statsData.animals_by_health_status.HEALTHY / ((animalsData?.length) || 1)) * 100)}%` 
          : statsData ? '0%' : 'N/A'
      });

      console.log('🎯 Estadísticas finales:', cattleStats);

    } catch (error) {
      console.error('❌ Error general loading cattle data:', error);
      setLoadError('Error al cargar los datos del ganado. Verifica la consola para más detalles.');
      
      // Establecer valores por defecto en caso de error
      setCattleStats({
        totalAnimals: 0,
        totalBatches: 0,
        totalCertifications: 0,
        healthStatus: 'N/A'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const quickActions = [
    {
      title: 'Registrar Animal',
      description: 'Agregar nuevo animal al sistema con todos sus datos',
      icon: <AnimalsIcon />,
      buttonText: 'Nuevo Animal',
      onClick: () => navigate('/animals?action=create'),
      color: 'primary' as const
    },
    {
      title: 'Crear Lote',
      description: 'Organizar animales en lotes para mejor gestión',
      icon: <BatchesIcon />,
      buttonText: 'Crear Lote',
      onClick: () => navigate('/batches?action=create'),
      color: 'secondary' as const
    },
    {
      title: 'Certificar',
      description: 'Gestionar certificaciones de calidad y origen',
      icon: <CertificationsIcon />,
      buttonText: 'Iniciar Certificación',
      onClick: () => navigate('/certifications?action=create'),
      color: 'success' as const
    }
  ];

  const refreshData = () => {
    loadCattleData();
  };

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

        {/* Error Alert */}
        {loadError && (
          <Alert 
            severity="error" 
            onClose={() => setLoadError(null)}
            action={
              <Button color="inherit" size="small" onClick={refreshData}>
                Reintentar
              </Button>
            }
            sx={{ mb: 3 }}
          >
            {loadError}
          </Alert>
        )}

        {/* Statistics Grid */}
        <Grid container spacing={3} className="stats-grid">
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <StatCard
              title="Total Animales"
              value={cattleStats.totalAnimals}
              icon={<AnimalsIcon />}
              color="primary"
              trend="+12%"
              loading={isLoading}
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <StatCard
              title="Lotes Activos"
              value={cattleStats.totalBatches}
              icon={<BatchesIcon />}
              color="secondary"
              loading={isLoading}
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <StatCard
              title="Certificaciones"
              value={cattleStats.totalCertifications}
              icon={<CertificationsIcon />}
              color="success"
              trend="+5%"
              loading={isLoading}
            />
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <StatCard
              title="Salud Promedio"
              value={cattleStats.healthStatus}
              icon={<AnalyticsIcon />}
              color="info"
              loading={isLoading}
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
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6" className="activity-title">
              Actividad Reciente
            </Typography>
            <Button 
              variant="outlined" 
              size="small" 
              onClick={refreshData}
              disabled={isLoading}
              startIcon={isLoading ? <CircularProgress size={16} /> : null}
            >
              Actualizar
            </Button>
          </Box>
          {isLoading ? (
            <Box display="flex" justifyContent="center" py={3}>
              <CircularProgress />
            </Box>
          ) : (
            <Typography variant="body2" className="activity-placeholder">
              {cattleStats.totalAnimals > 0 
                ? `Sistema activo con ${cattleStats.totalAnimals} animales y ${cattleStats.totalBatches} lotes registrados.`
                : 'Aquí se mostrará el historial de actividades recientes del sistema...'
              }
            </Typography>
          )}
        </Paper>
      </Box>
    </DashboardLayout>
  );
};

export default Dashboard;