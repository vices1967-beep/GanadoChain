// src/features/cattle/components/AnimalList.tsx
import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Box,
  Typography
} from '@mui/material';
import {
  Visibility as ViewIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Pets as AnimalIcon
} from '@mui/icons-material';
import { Animal } from '../../../types/domain/cattle';

interface AnimalListProps {
  animals: Animal[];
  loading: boolean;
  onViewAnimal: (animal: Animal) => void;
  onEditAnimal: (animal: Animal) => void;
  onDeleteAnimal: (id: number) => void;
}

const AnimalList: React.FC<AnimalListProps> = ({
  animals,
  loading,
  onViewAnimal,
  onEditAnimal,
  onDeleteAnimal
}) => {
  const getHealthStatusColor = (status: string) => {
    switch (status) {
      case 'EXCELLENT': return 'success';
      case 'GOOD': return 'info';
      case 'FAIR': return 'warning';
      case 'POOR': return 'error';
      case 'CRITICAL': return 'error';
      default: return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE': return 'success';
      case 'SOLD': return 'warning';
      case 'DECEASED': return 'error';
      case 'QUARANTINED': return 'warning';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <Typography>Cargando animales...</Typography>
      </Box>
    );
  }

  if (animals.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px" flexDirection="column">
        <AnimalIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h6" color="text.secondary">
          No hay animales registrados
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Comienza agregando tu primer animal al sistema
        </Typography>
      </Box>
    );
  }

  return (
    <TableContainer component={Paper}>
      <Table sx={{ minWidth: 650 }} aria-label="tabla de animales">
        <TableHead>
          <TableRow>
            <TableCell>Arete</TableCell>
            <TableCell>Nombre</TableCell>
            <TableCell>Raza</TableCell>
            <TableCell>Peso (kg)</TableCell>
            <TableCell>Salud</TableCell>
            <TableCell>Estado</TableCell>
            <TableCell>Ubicación</TableCell>
            <TableCell align="center">Acciones</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {animals.map((animal) => (
            <TableRow key={animal.id} hover>
              <TableCell>
                <Box display="flex" alignItems="center">
                  <AnimalIcon sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography fontWeight="bold">{animal.ear_tag}</Typography>
                </Box>
              </TableCell>
              <TableCell>{animal.name}</TableCell>
              <TableCell>{animal.breed}</TableCell>
              <TableCell>{animal.weight}</TableCell>
              <TableCell>
                <Chip
                  label={animal.health_status}
                  color={getHealthStatusColor(animal.health_status) as any}
                  size="small"
                />
              </TableCell>
              <TableCell>
                <Chip
                  label={animal.status}
                  color={getStatusColor(animal.status) as any}
                  size="small"
                />
              </TableCell>
              <TableCell>{animal.location}</TableCell>
              <TableCell align="center">
                <IconButton
                  size="small"
                  onClick={() => onViewAnimal(animal)}
                  color="info"
                >
                  <ViewIcon />
                </IconButton>
                <IconButton
                  size="small"
                  onClick={() => onEditAnimal(animal)}
                  color="primary"
                >
                  <EditIcon />
                </IconButton>
                <IconButton
                  size="small"
                  onClick={() => onDeleteAnimal(animal.id)}
                  color="error"
                >
                  <DeleteIcon />
                </IconButton>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default AnimalList;