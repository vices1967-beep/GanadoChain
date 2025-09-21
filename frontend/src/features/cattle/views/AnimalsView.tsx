// src/features/cattle/views/AnimalsView.tsx
import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Container,
  Typography,
  Paper,
  Grid
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { useCattleContext } from '../../../contexts/cattle/CattleContext';
import AnimalList from '../components/AnimalList';
import AnimalForm from '../components/AnimalForm';
import AnimalDetail from '../components/AnimalDetail';
import CattleStats from '../components/CattleStats';

const AnimalsView: React.FC = () => {
  const {
    animals,
    loading,
    getAnimals,
    createAnimal,
    updateAnimal,
    deleteAnimal,
    stats,
    getStats
  } = useCattleContext();

  const [formOpen, setFormOpen] = useState(false);
  const [detailOpen, setDetailOpen] = useState(false);
  const [selectedAnimal, setSelectedAnimal] = useState<any>(null);
  const [editingAnimal, setEditingAnimal] = useState<any>(null);

  useEffect(() => {
    getAnimals();
    getStats();
  }, []);

  const handleCreateAnimal = async (data: any) => {
    await createAnimal(data);
    getAnimals();
    getStats();
  };

  const handleUpdateAnimal = async (data: any) => {
    if (editingAnimal) {
      await updateAnimal(editingAnimal.id, data);
      setEditingAnimal(null);
      getAnimals();
      getStats();
    }
  };

  const handleDeleteAnimal = async (id: number) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este animal?')) {
      await deleteAnimal(id);
      getAnimals();
      getStats();
    }
  };

  const handleViewAnimal = (animal: any) => {
    setSelectedAnimal(animal);
    setDetailOpen(true);
  };

  const handleEditAnimal = (animal: any) => {
    setEditingAnimal(animal);
    setFormOpen(true);
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Gestión de Animales
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Administra el inventario de ganado y su información
        </Typography>
      </Box>

      {/* Estadísticas */}
      {stats && (
        <Box sx={{ mb: 4 }}>
          <CattleStats stats={stats} />
        </Box>
      )}

      <Grid container spacing={3}>
        <Grid size={{ xs: 12 }}>
          <Paper sx={{ p: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
              <Typography variant="h6">
                Lista de Animales ({animals.length})
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setFormOpen(true)}
              >
                Nuevo Animal
              </Button>
            </Box>

            <AnimalList
              animals={animals}
              loading={loading}
              onViewAnimal={handleViewAnimal}
              onEditAnimal={handleEditAnimal}
              onDeleteAnimal={handleDeleteAnimal}
            />
          </Paper>
        </Grid>
      </Grid>

      {/* Modal de Formulario */}
      <AnimalForm
        open={formOpen}
        onClose={() => {
          setFormOpen(false);
          setEditingAnimal(null);
        }}
        onSubmit={editingAnimal ? handleUpdateAnimal : handleCreateAnimal}
        initialData={editingAnimal}
        loading={loading}
      />

      {/* Modal de Detalle */}
      <AnimalDetail
        open={detailOpen}
        onClose={() => {
          setDetailOpen(false);
          setSelectedAnimal(null);
        }}
        animal={selectedAnimal}
      />
    </Container>
  );
};

export default AnimalsView;