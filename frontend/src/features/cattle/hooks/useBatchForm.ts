// src/features/cattle/hooks/useBatchForm.ts
import { useState } from 'react';
import { BatchCreateRequest } from '../../../types/domain/cattle';

export const useBatchForm = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (
    data: BatchCreateRequest,
    onSubmit: (data: BatchCreateRequest) => Promise<void>,
    onSuccess?: () => void
  ) => {
    setLoading(true);
    setError(null);
    
    try {
      await onSubmit(data);
      onSuccess?.();
    } catch (err: any) {
      setError(err.message || 'Error al guardar el lote');
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