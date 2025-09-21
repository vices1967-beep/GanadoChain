// src/features/cattle/components/HealthRecords.tsx
import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Divider,
  Grid
} from '@mui/material';
import {
  MedicalServices as MedicalIcon,
  CalendarToday as DateIcon,
  Person as VetIcon
} from '@mui/icons-material';
import { AnimalHealthRecord } from '../../../types/domain/cattle';

interface HealthRecordsProps {
  records: AnimalHealthRecord[];
  loading: boolean;
}

const HealthRecords: React.FC<HealthRecordsProps> = ({ records, loading }) => {
  const getSourceColor = (source: string) => {
    switch (source) {
      case 'VETERINARIAN': return 'primary';
      case 'FARMER': return 'secondary';
      case 'IOT': return 'info';
      case 'SYSTEM': return 'default';
      default: return 'default';
    }
  };

  const getSourceLabel = (source: string) => {
    switch (source) {
      case 'VETERINARIAN': return 'Veterinario';
      case 'FARMER': return 'Ganadero';
      case 'IOT': return 'Dispositivo IoT';
      case 'SYSTEM': return 'Sistema';
      default: return source;
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <Typography>Cargando registros de salud...</Typography>
      </Box>
    );
  }

  if (records.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px" flexDirection="column">
        <MedicalIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h6" color="text.secondary">
          No hay registros de salud
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Añade registros de salud para este animal
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      {records.map((record) => (
        <Card key={record.id} sx={{ mb: 2 }}>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
              <Box>
                <Typography variant="h6" gutterBottom>
                  {record.diagnosis}
                </Typography>
                <Box display="flex" alignItems="center" mb={1}>
                  <DateIcon sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
                  <Typography variant="body2" color="text.secondary">
                    {new Date(record.examination_date).toLocaleDateString()}
                  </Typography>
                </Box>
                {record.veterinarian && (
                  <Box display="flex" alignItems="center">
                    <VetIcon sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
                    <Typography variant="body2" color="text.secondary">
                      Veterinario #{record.veterinarian}
                    </Typography>
                  </Box>
                )}
              </Box>
              <Chip
                label={getSourceLabel(record.source)}
                color={getSourceColor(record.source) as any}
                size="small"
              />
            </Box>

            <Divider sx={{ my: 2 }} />

            <Grid container spacing={2}>
              <Grid size={{ xs: 12, md: 6 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Tratamiento
                </Typography>
                <Typography variant="body2">
                  {record.treatment}
                </Typography>
              </Grid>
              <Grid size={{ xs: 12, md: 6 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Medicación
                </Typography>
                <Typography variant="body2">
                  {record.medication}
                </Typography>
              </Grid>
              {record.notes && (
                <Grid size={{ xs: 12 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Notas
                  </Typography>
                  <Typography variant="body2">
                    {record.notes}
                  </Typography>
                </Grid>
              )}
            </Grid>

            {(record.temperature || record.heart_rate || record.respiratory_rate || record.weight) && (
              <>
                <Divider sx={{ my: 2 }} />
                <Grid container spacing={2}>
                  {record.temperature && (
                    <Grid size={{ xs: 6, sm: 3 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Temperatura
                      </Typography>
                      <Typography variant="body2">
                        {record.temperature}°C
                      </Typography>
                    </Grid>
                  )}
                  {record.heart_rate && (
                    <Grid size={{ xs: 6, sm: 3 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Ritmo Cardíaco
                      </Typography>
                      <Typography variant="body2">
                        {record.heart_rate} BPM
                      </Typography>
                    </Grid>
                  )}
                  {record.respiratory_rate && (
                    <Grid size={{ xs: 6, sm: 3 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Ritmo Respiratorio
                      </Typography>
                      <Typography variant="body2">
                        {record.respiratory_rate} RPM
                      </Typography>
                    </Grid>
                  )}
                  {record.weight && (
                    <Grid size={{ xs: 6, sm: 3 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Peso
                      </Typography>
                      <Typography variant="body2">
                        {record.weight} kg
                      </Typography>
                    </Grid>
                  )}
                </Grid>
              </>
            )}
          </CardContent>
        </Card>
      ))}
    </Box>
  );
};

export default HealthRecords;