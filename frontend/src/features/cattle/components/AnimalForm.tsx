// src/features/cattle/components/AnimalForm.tsx
import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Grid,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Box,
  Typography
} from '@mui/material';
import { useFormik } from 'formik';
import * as yup from 'yup';
import { Animal, AnimalCreateRequest } from '../../../types/domain/cattle';

interface AnimalFormProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: AnimalCreateRequest) => Promise<void>;
  initialData?: Animal;
  loading?: boolean;
}

const validationSchema = yup.object({
  ear_tag: yup.string().required('El arete es requerido'),
  name: yup.string().required('El nombre es requerido'),
  breed: yup.string().required('La raza es requerida'),
  birth_date: yup.string().required('La fecha de nacimiento es requerida'),
  gender: yup.string().oneOf(['M', 'F']).required('El género es requerido'),
  weight: yup.number().min(0).required('El peso es requerido'),
  health_status: yup.string().required('El estado de salud es requerido'),
  location: yup.string().required('La ubicación es requerida')
});

const AnimalForm: React.FC<AnimalFormProps> = ({
  open,
  onClose,
  onSubmit,
  initialData,
  loading = false
}) => {
  const formik = useFormik({
    initialValues: {
      ear_tag: initialData?.ear_tag || '',
      name: initialData?.name || '',
      breed: initialData?.breed || '',
      birth_date: initialData?.birth_date || '',
      gender: initialData?.gender || 'M',
      weight: initialData?.weight || 0,
      health_status: initialData?.health_status || 'GOOD',
      location: initialData?.location || '',
      mother: initialData?.mother || undefined,
      father: initialData?.father || undefined
    },
    validationSchema,
    onSubmit: async (values) => {
      await onSubmit(values);
      formik.resetForm();
      onClose();
    },
    enableReinitialize: true
  });

  const healthStatusOptions = [
    { value: 'EXCELLENT', label: 'Excelente' },
    { value: 'GOOD', label: 'Buena' },
    { value: 'FAIR', label: 'Regular' },
    { value: 'POOR', label: 'Mala' },
    { value: 'CRITICAL', label: 'Crítica' }
  ];

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Typography variant="h6">
          {initialData ? 'Editar Animal' : 'Nuevo Animal'}
        </Typography>
      </DialogTitle>
      <form onSubmit={formik.handleSubmit}>
        <DialogContent>
          <Box sx={{ mt: 1 }}>
            <Grid container spacing={2}>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Número de Arete"
                  name="ear_tag"
                  value={formik.values.ear_tag}
                  onChange={formik.handleChange}
                  error={formik.touched.ear_tag && Boolean(formik.errors.ear_tag)}
                  helperText={formik.touched.ear_tag && formik.errors.ear_tag}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Nombre"
                  name="name"
                  value={formik.values.name}
                  onChange={formik.handleChange}
                  error={formik.touched.name && Boolean(formik.errors.name)}
                  helperText={formik.touched.name && formik.errors.name}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Raza"
                  name="breed"
                  value={formik.values.breed}
                  onChange={formik.handleChange}
                  error={formik.touched.breed && Boolean(formik.errors.breed)}
                  helperText={formik.touched.breed && formik.errors.breed}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Fecha de Nacimiento"
                  name="birth_date"
                  type="date"
                  InputLabelProps={{ shrink: true }}
                  value={formik.values.birth_date}
                  onChange={formik.handleChange}
                  error={formik.touched.birth_date && Boolean(formik.errors.birth_date)}
                  helperText={formik.touched.birth_date && formik.errors.birth_date}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <FormControl fullWidth>
                  <InputLabel>Género</InputLabel>
                  <Select
                    name="gender"
                    value={formik.values.gender}
                    onChange={formik.handleChange}
                    label="Género"
                  >
                    <MenuItem value="M">Macho</MenuItem>
                    <MenuItem value="F">Hembra</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Peso (kg)"
                  name="weight"
                  type="number"
                  value={formik.values.weight}
                  onChange={formik.handleChange}
                  error={formik.touched.weight && Boolean(formik.errors.weight)}
                  helperText={formik.touched.weight && formik.errors.weight}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <FormControl fullWidth>
                  <InputLabel>Estado de Salud</InputLabel>
                  <Select
                    name="health_status"
                    value={formik.values.health_status}
                    onChange={formik.handleChange}
                    label="Estado de Salud"
                  >
                    {healthStatusOptions.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <TextField
                  fullWidth
                  label="Ubicación"
                  name="location"
                  value={formik.values.location}
                  onChange={formik.handleChange}
                  error={formik.touched.location && Boolean(formik.errors.location)}
                  helperText={formik.touched.location && formik.errors.location}
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose} disabled={loading}>
            Cancelar
          </Button>
          <Button type="submit" variant="contained" disabled={loading}>
            {loading ? 'Guardando...' : initialData ? 'Actualizar' : 'Crear'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default AnimalForm;