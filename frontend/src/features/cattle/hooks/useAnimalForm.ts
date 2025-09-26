// src/features/cattle/hooks/useAnimalForm.ts
import { useState } from 'react';
import { AnimalCreateRequest } from '../../../types/domain/cattle'; // Eliminada la importación no utilizada

export const useAnimalForm = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (
    data: AnimalCreateRequest,
    onSubmit: (data: AnimalCreateRequest) => Promise<void>,
    onSuccess?: () => void
  ) => {
    setLoading(true);
    setError(null);
    
    try {
      await onSubmit(data);
      onSuccess?.();
    } catch (err: any) {
      setError(err.message || 'Error al guardar el animal');
    } finally {
      setLoading(false);
    }
  };

  return {
    loading,
    error,
    handleSubmit,
    clearError: () => setError(null)
  };
};