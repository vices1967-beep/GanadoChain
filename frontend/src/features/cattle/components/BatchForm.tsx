// src/features/cattle/components/BatchForm.tsx
import React, { useState, useEffect } from 'react';
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
  Typography,
  Chip,
  Autocomplete
} from '@mui/material';
import { useFormik } from 'formik';
import * as yup from 'yup';
import { BatchCreateRequest } from '../../../types/domain/cattle';
import { useCattleContext } from '../../../contexts/cattle/CattleContext';

interface BatchFormProps {
  open: boolean;
  onClose: () => void; // Corregido: función que devuelve void
  onSubmit: (data: BatchCreateRequest) => Promise<void>;
  initialData?: any;
  loading?: boolean;
}

const validationSchema = yup.object({
  name: yup.string().required('El nombre es requerido'),
  description: yup.string().required('La descripción es requerida'),
  status: yup.string().required('El estado es requerido')
});

const BatchForm: React.FC<BatchFormProps> = ({
  open,
  onClose,
  onSubmit,
  initialData,
  loading = false
}) => {
  const { animals, getAnimals } = useCattleContext();
  const [selectedAnimals, setSelectedAnimals] = useState<any[]>([]);

  useEffect(() => {
    if (open) {
      getAnimals();
      if (initialData) {
        setSelectedAnimals(initialData.animals || []);
      }
    }
  }, [open, initialData]);

  const formik = useFormik({
    initialValues: {
      name: initialData?.name || '',
      description: initialData?.description || '',
      status: initialData?.status || 'ACTIVE',
      animals: initialData?.animals || []
    },
    validationSchema,
    onSubmit: async (values) => {
      const submitData = {
        ...values,
        animals: selectedAnimals.map(animal => animal.id)
      };
      await onSubmit(submitData);
      formik.resetForm();
      setSelectedAnimals([]);
      onClose(); // Esto ahora funciona porque onClose es una función
    },
    enableReinitialize: true
  });

  const statusOptions = [
    { value: 'ACTIVE', label: 'Activo' },
    { value: 'INACTIVE', label: 'Inactivo' },
    { value: 'SOLD', label: 'Vendido' },
    { value: 'QUARANTINED', label: 'Cuarentena' }
  ];

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Typography variant="h6">
          {initialData ? 'Editar Lote' : 'Nuevo Lote'}
        </Typography>
      </DialogTitle>
      <form onSubmit={formik.handleSubmit}>
        <DialogContent>
          <Box sx={{ mt: 1 }}>
            <Grid container spacing={2}>
              <Grid size={{ xs: 12 }}>
                <TextField
                  fullWidth
                  label="Nombre del Lote"
                  name="name"
                  value={formik.values.name}
                  onChange={formik.handleChange}
                  error={formik.touched.name && Boolean(formik.errors.name)}
                  helperText={formik.touched.name && formik.errors.name as string}
                />
              </Grid>
              <Grid size={{ xs: 12 }}>
                <TextField
                  fullWidth
                  label="Descripción"
                  name="description"
                  multiline
                  rows={3}
                  value={formik.values.description}
                  onChange={formik.handleChange}
                  error={formik.touched.description && Boolean(formik.errors.description)}
                  helperText={formik.touched.description && formik.errors.description as string}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 6 }}>
                <FormControl fullWidth>
                  <InputLabel>Estado</InputLabel>
                  <Select
                    name="status"
                    value={formik.values.status}
                    onChange={formik.handleChange}
                    label="Estado"
                  >
                    {statusOptions.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid size={{ xs: 12 }}>
                <Autocomplete
                  multiple
                  options={animals}
                  getOptionLabel={(option) => `${option.ear_tag} - ${option.name}`}
                  value={selectedAnimals}
                  onChange={(_, newValue) => { // Eliminado el parámetro event no utilizado
                    setSelectedAnimals(newValue);
                  }}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Seleccionar Animales"
                      placeholder="Buscar animales..."
                    />
                  )}
                  renderTags={(value, getTagProps) =>
                    value.map((option, index) => (
                      <Chip
                        {...getTagProps({ index })}
                        key={option.id}
                        label={`${option.ear_tag} - ${option.name}`}
                        size="small"
                      />
                    ))
                  }
                />
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
                  {selectedAnimals.length} animales seleccionados
                </Typography>
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

export default BatchForm;