// src/features/cattle/components/CertificationList.tsx
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
  Block as RevokeIcon,
  Assignment as CertificationIcon
} from '@mui/icons-material';
import { AnimalCertification } from '../../../types/domain/cattle';

interface CertificationListProps {
  certifications: AnimalCertification[];
  loading: boolean;
  onViewCertification: (certification: AnimalCertification) => void;
  onEditCertification: (certification: AnimalCertification) => void;
  onRevokeCertification: (id: number) => void;
}

const CertificationList: React.FC<CertificationListProps> = ({
  certifications,
  loading,
  onViewCertification,
  onEditCertification,
  onRevokeCertification
}) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE': return 'success';
      case 'EXPIRED': return 'warning';
      case 'REVOKED': return 'error';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <Typography>Cargando certificaciones...</Typography>
      </Box>
    );
  }

  if (certifications.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px" flexDirection="column">
        <CertificationIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h6" color="text.secondary">
          No hay certificaciones
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Añade certificaciones a los animales
        </Typography>
      </Box>
    );
  }

  return (
    <TableContainer component={Paper}>
      <Table sx={{ minWidth: 650 }} aria-label="tabla de certificaciones">
        <TableHead>
          <TableRow>
            <TableCell>Animal</TableCell>
            <TableCell>Certificación</TableCell>
            <TableCell>Fecha Emisión</TableCell>
            <TableCell>Fecha Expiración</TableCell>
            <TableCell>Organismo</TableCell>
            <TableCell>Estado</TableCell>
            <TableCell align="center">Acciones</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {certifications.map((certification) => (
            <TableRow key={certification.id} hover>
              <TableCell>
                <Typography fontWeight="bold">
                  Animal #{certification.animal}
                </Typography>
              </TableCell>
              <TableCell>
                <Typography>Estándar #{certification.standard}</Typography>
              </TableCell>
              <TableCell>
                {new Date(certification.certification_date).toLocaleDateString()}
              </TableCell>
              <TableCell>
                {new Date(certification.expiration_date).toLocaleDateString()}
              </TableCell>
              <TableCell>{certification.certifying_body}</TableCell>
              <TableCell>
                <Chip
                  label={certification.status}
                  color={getStatusColor(certification.status) as any}
                  size="small"
                />
              </TableCell>
              <TableCell align="center">
                <IconButton
                  size="small"
                  onClick={() => onViewCertification(certification)}
                  color="info"
                >
                  <ViewIcon />
                </IconButton>
                <IconButton
                  size="small"
                  onClick={() => onEditCertification(certification)}
                  color="primary"
                >
                  <EditIcon />
                </IconButton>
                {certification.status === 'ACTIVE' && (
                  <IconButton
                    size="small"
                    onClick={() => onRevokeCertification(certification.id)}
                    color="error"
                  >
                    <RevokeIcon />
                  </IconButton>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default CertificationList;