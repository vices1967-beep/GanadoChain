// src/features/cattle/views/CertificationsView.tsx
import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Container,
  Typography,
  Paper
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
//import { useCattleContext } from '../../../contexts/cattle/CattleContext';
import { useCattle } from '../../../hooks/cattle/useCattle';
import CertificationList from '../components/CertificationList';

const CertificationsView: React.FC = () => {
  const {
    certifications,
    loading,
    getAnimalCertifications,
    revokeCertification
  } = useCattle();

  const [selectedAnimalId] = useState<number | null>(null); // Eliminado setSelectedAnimalId

  useEffect(() => {
    // La función getAnimalCertifications espera un número, no undefined
    // Si selectedAnimalId es null, no llamamos a la función
    if (selectedAnimalId !== null) {
      getAnimalCertifications(selectedAnimalId);
    } else {
      // Si no hay animal seleccionado, podríamos cargar todas las certificaciones
      // o mantener la lista vacía. Depende de la lógica de negocio.
      // Por ahora, dejamos la lista vacía si no hay animal seleccionado
    }
  }, [selectedAnimalId]);

  const handleViewCertification = (certification: any) => {
    console.log('View certification:', certification);
  };

  const handleEditCertification = (certification: any) => {
    console.log('Edit certification:', certification);
  };

  const handleRevokeCertification = async (id: number) => {
    if (window.confirm('¿Estás seguro de que quieres revocar esta certificación?')) {
      await revokeCertification(id, 'Revocación manual');
      // Recargar certificaciones después de revocar solo si hay un animal seleccionado
      if (selectedAnimalId !== null) {
        getAnimalCertifications(selectedAnimalId);
      }
    }
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Certificaciones
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Gestiona las certificaciones de calidad y origen
        </Typography>
      </Box>

      <Paper sx={{ p: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h6">
            Lista de Certificaciones ({certifications.length})
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => {}}
          >
            Nueva Certificación
          </Button>
        </Box>

        <CertificationList
          certifications={certifications}
          loading={loading}
          onViewCertification={handleViewCertification}
          onEditCertification={handleEditCertification}
          onRevokeCertification={handleRevokeCertification}
        />
      </Paper>
    </Container>
  );
};

export default CertificationsView;