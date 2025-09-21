// src/features/cattle/views/BatchesView.tsx
import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Container,
  Typography,
  Paper
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { useCattleContext } from '../../../contexts/cattle/CattleContext';
import BatchList from '../components/BatchList';
import BatchForm from '../components/BatchForm';

const BatchesView: React.FC = () => {
  const {
    batches,
    loading,
    getBatches,
    createBatch
  } = useCattleContext();

  const [formOpen, setFormOpen] = useState(false);

  useEffect(() => {
    getBatches();
  }, []);

  const handleCreateBatch = async (data: any) => {
    await createBatch(data);
    getBatches();
  };

  const handleViewBatch = (batch: any) => {
    console.log('View batch:', batch);
  };

  const handleEditBatch = (batch: any) => {
    // Función vacía ya que no hay funcionalidad de edición
    console.log('Edit batch:', batch);
  };

  const handleDeleteBatch = (id: number) => {
    // Función vacía ya que no hay funcionalidad de eliminación
    console.log('Delete batch:', id);
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Gestión de Lotes
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Organiza los animales en lotes para mejor gestión
        </Typography>
      </Box>

      <Paper sx={{ p: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h6">
            Lista de Lotes ({batches.length})
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setFormOpen(true)}
          >
            Nuevo Lote
          </Button>
        </Box>

        <BatchList
          batches={batches}
          loading={loading}
          onViewBatch={handleViewBatch}
          onEditBatch={handleEditBatch}
          onDeleteBatch={handleDeleteBatch}
        />
      </Paper>

      <BatchForm
        open={formOpen}
        onClose={() => {
          setFormOpen(false);
        }}
        onSubmit={handleCreateBatch}
        initialData={null}
        loading={loading}
      />
    </Container>
  );
};

export default BatchesView;