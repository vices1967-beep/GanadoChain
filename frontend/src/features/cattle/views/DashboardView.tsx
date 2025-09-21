// src/features/cattle/views/DashboardView.tsx
import React, { useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box
} from '@mui/material';
import {
  Pets as AnimalsIcon,
  Groups as BatchesIcon,
  Assignment as CertsIcon,
  ShowChart as StatsIcon
} from '@mui/icons-material';
//import { useCattleContext } from '../../../contexts/cattle/CattleContext';
import { useCattle } from '../../../hooks/cattle/useCattle';
import CattleStats from '../components/CattleStats';

const DashboardView: React.FC = () => {
  const { stats, getStats, animals, batches, certifications, getAnimals, getBatches } = useCattle();

  useEffect(() => {
    getStats();
    getAnimals();
    getBatches();
  }, []);

  // Asegurarse de que animals, batches y certifications sean arrays
  const safeAnimals = animals || [];
  const safeBatches = batches || [];
  const safeCertifications = certifications || [];

  const quickStats = [
    {
      title: 'Total Animales',
      value: safeAnimals.length,
      icon: <AnimalsIcon sx={{ fontSize: 40 }} />,
      color: 'primary.main'
    },
    {
      title: 'Lotes Activos',
      value: safeBatches.length,
      icon: <BatchesIcon sx={{ fontSize: 40 }} />,
      color: 'secondary.main'
    },
    {
      title: 'Certificaciones',
      value: safeCertifications.length,
      icon: <CertsIcon sx={{ fontSize: 40 }} />,
      color: 'success.main'
    },
    {
      title: 'Salud Promedio',
      value: 'Buena',
      icon: <StatsIcon sx={{ fontSize: 40 }} />,
      color: 'info.main'
    }
  ];

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Dashboard de Ganado
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Resumen general del estado de tu ganado
        </Typography>
      </Box>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        {quickStats.map((stat, index) => (
          <Grid size={{ xs: 12, sm: 6, md: 3 }} key={index}>
            <Paper
              sx={{
                p: 3,
                bgcolor: stat.color,
                color: 'white',
                textAlign: 'center'
              }}
            >
              <Box sx={{ opacity: 0.8, mb: 2 }}>
                {stat.icon}
              </Box>
              <Typography variant="h3" fontWeight="bold" gutterBottom>
                {stat.value}
              </Typography>
              <Typography variant="body2">
                {stat.title}
              </Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>

      {stats && (
        <Grid container spacing={3}>
          <Grid size={{ xs: 12 }}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Estadísticas Detalladas
              </Typography>
              <CattleStats stats={stats} />
            </Paper>
          </Grid>
        </Grid>
      )}
    </Container>
  );
};

export default DashboardView;