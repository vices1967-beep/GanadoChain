// src/features/cattle/components/BatchList.tsx
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
  Typography,
  Avatar,
  AvatarGroup
} from '@mui/material';
import {
  Visibility as ViewIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Groups as BatchIcon,
  Pets as AnimalIcon
} from '@mui/icons-material';
import { Batch } from '../../../types/domain/cattle';

interface BatchListProps {
  batches: Batch[];
  loading: boolean;
  onViewBatch: (batch: Batch) => void;
  onEditBatch: (batch: Batch) => void;
  onDeleteBatch: (id: number) => void;
}

const BatchList: React.FC<BatchListProps> = ({
  batches,
  loading,
  onViewBatch,
  onEditBatch,
  onDeleteBatch
}) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE': return 'success';
      case 'INACTIVE': return 'default';
      case 'SOLD': return 'warning';
      case 'QUARANTINED': return 'error';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <Typography>Cargando lotes...</Typography>
      </Box>
    );
  }

  if (batches.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px" flexDirection="column">
        <BatchIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h6" color="text.secondary">
          No hay lotes registrados
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Crea tu primer lote para organizar los animales
        </Typography>
      </Box>
    );
  }

  return (
    <TableContainer component={Paper}>
      <Table sx={{ minWidth: 650 }} aria-label="tabla de lotes">
        <TableHead>
          <TableRow>
            <TableCell>Nombre</TableCell>
            <TableCell>Descripción</TableCell>
            <TableCell>Animales</TableCell>
            <TableCell>Estado</TableCell>
            <TableCell>Blockchain</TableCell>
            <TableCell align="center">Acciones</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {batches.map((batch) => (
            <TableRow key={batch.id} hover>
              <TableCell>
                <Box display="flex" alignItems="center">
                  <BatchIcon sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography fontWeight="bold">{batch.name}</Typography>
                </Box>
              </TableCell>
              <TableCell>
                <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                  {batch.description}
                </Typography>
              </TableCell>
              <TableCell>
                <Box display="flex" alignItems="center">
                  <AvatarGroup max={4} sx={{ mr: 2 }}>
                    {batch.animals.slice(0, 4).map((_, index) => ( // Cambiado animalId por _
                      <Avatar key={index} sx={{ width: 32, height: 32 }}>
                        <AnimalIcon fontSize="small" />
                      </Avatar>
                    ))}
                  </AvatarGroup>
                  <Typography variant="body2">
                    {batch.animals.length} animales
                  </Typography>
                </Box>
              </TableCell>
              <TableCell>
                <Chip
                  label={batch.status}
                  color={getStatusColor(batch.status) as any}
                  size="small"
                />
              </TableCell>
              <TableCell>
                <Chip
                  label={batch.on_blockchain ? 'Sincronizado' : 'Pendiente'}
                  color={batch.on_blockchain ? 'success' : 'default'}
                  size="small"
                />
              </TableCell>
              <TableCell align="center">
                <IconButton
                  size="small"
                  onClick={() => onViewBatch(batch)}
                  color="info"
                >
                  <ViewIcon />
                </IconButton>
                <IconButton
                  size="small"
                  onClick={() => onEditBatch(batch)}
                  color="primary"
                >
                  <EditIcon />
                </IconButton>
                <IconButton
                  size="small"
                  onClick={() => onDeleteBatch(batch.id)}
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

export default BatchList;