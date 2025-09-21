// src/features/cattle/views/HealthView.tsx
import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  Chip
} from '@mui/material';
import {
  MedicalServices as HealthIcon
} from '@mui/icons-material';
import { useCattle } from '../../../hooks/cattle/useCattle';
import HealthRecords from '../components/HealthRecords';
import { AnimalHealthRecord } from '../../../types/domain/cattle';

const HealthView: React.FC = () => {
  const { animals, getAnimals, getAnimalHealthRecords } = useCattle();
  const [healthRecords, setHealthRecords] = useState<AnimalHealthRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedAnimal] = useState<number | null>(null);

  useEffect(() => {
    getAnimals();
  }, []);

  useEffect(() => {
    if (selectedAnimal) {
      loadHealthRecords(selectedAnimal);
    }
  }, [selectedAnimal]);

  const loadHealthRecords = async (animalId: number) => {
    setLoading(true);
    try {
      // getAnimalHealthRecords devuelve una acción de Redux, necesitamos await y .unwrap()
      const records = await getAnimalHealthRecords(animalId);
      setHealthRecords(records);
    } catch (error) {
      console.error('Error loading health records:', error);
      setHealthRecords([]);
    } finally {
      setLoading(false);
    }
  };

  const animalsByHealth = animals.reduce((acc, animal) => {
    acc[animal.health_status] = (acc[animal.health_status] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Salud del Ganado
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Monitorea el estado de salud de tus animales
        </Typography>
      </Box>

      <Grid container spacing={3}>
        <Grid size={{ xs: 12 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Resumen de Salud
            </Typography>
            <Grid container spacing={2}>
              {Object.entries(animalsByHealth).map(([status, count]) => (
                <Grid size={{ xs: 6, sm: 3 }} key={status}>
                  <Card>
                    <CardContent sx={{ textAlign: 'center' }}>
                      <HealthIcon
                        sx={{
                          fontSize: 40,
                          color: status === 'CRITICAL' || status === 'POOR' ? 'error.main' : 
                                 status === 'FAIR' ? 'warning.main' : 'success.main'
                        }}
                      />
                      <Typography variant="h4" gutterBottom>
                        {count}
                      </Typography>
                      <Chip
                        label={status}
                        color={
                          status === 'CRITICAL' || status === 'POOR' ? 'error' :
                          status === 'FAIR' ? 'warning' : 'success'
                        }
                      />
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Grid>

        <Grid size={{ xs: 12 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Registros de Salud
            </Typography>
            <HealthRecords records={healthRecords} loading={loading} />
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default HealthView;