// src/features/cattle/components/AnimalDetail.tsx
import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  Box,
  Typography,
  Grid,
  Chip,
  Divider,
  Card,
  CardContent,
  IconButton
} from '@mui/material';
import {
  Close as CloseIcon,
  Pets as AnimalIcon,
  Scale as WeightIcon,
  Cake as BirthIcon,
  Female as FemaleIcon,
  Male as MaleIcon,
  LocationOn as LocationIcon
} from '@mui/icons-material';
import { Animal } from '../../../types/domain/cattle';

interface AnimalDetailProps {
  open: boolean;
  onClose: () => void;
  animal: Animal | null;
}

const AnimalDetail: React.FC<AnimalDetailProps> = ({ open, onClose, animal }) => {
  if (!animal) return null;

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

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">Detalle del Animal</Typography>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      <DialogContent>
        <Grid container spacing={3}>
          <Grid size={{ xs: 12 }}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <AnimalIcon sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
                  <Box>
                    <Typography variant="h5" gutterBottom>
                      {animal.name}
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                      Arete: {animal.ear_tag}
                    </Typography>
                  </Box>
                </Box>

                <Grid container spacing={2}>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <Box display="flex" alignItems="center" mb={1}>
                      {animal.gender === 'F' ? <FemaleIcon /> : <MaleIcon />}
                      <Typography variant="body2" sx={{ ml: 1 }}>
                        {animal.gender === 'F' ? 'Hembra' : 'Macho'}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <Box display="flex" alignItems="center" mb={1}>
                      <WeightIcon />
                      <Typography variant="body2" sx={{ ml: 1 }}>
                        {animal.weight} kg
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <Box display="flex" alignItems="center" mb={1}>
                      <BirthIcon />
                      <Typography variant="body2" sx={{ ml: 1 }}>
                        {new Date(animal.birth_date).toLocaleDateString()}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <Box display="flex" alignItems="center" mb={1}>
                      <LocationIcon />
                      <Typography variant="body2" sx={{ ml: 1 }}>
                        {animal.location}
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>

                <Divider sx={{ my: 2 }} />

                <Box display="flex" gap={1} flexWrap="wrap">
                  <Chip
                    label={`Salud: ${animal.health_status}`}
                    color={getHealthStatusColor(animal.health_status) as any}
                  />
                  <Chip
                    label={`Estado: ${animal.status}`}
                    color={getStatusColor(animal.status) as any}
                  />
                  <Chip
                    label={animal.breed}
                    variant="outlined"
                  />
                </Box>

                {animal.token_id && (
                  <Box mt={2}>
                    <Typography variant="subtitle2" gutterBottom>
                      Blockchain NFT
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Token ID: {animal.token_id}
                    </Typography>
                    {animal.nft_owner_wallet && (
                      <Typography variant="body2" color="text.secondary">
                        Propietario: {animal.nft_owner_wallet}
                      </Typography>
                    )}
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </DialogContent>
    </Dialog>
  );
};

export default AnimalDetail;