// src/hooks/cattle/useBatchOperations.ts
import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { Batch, BatchCreateRequest } from '../../types/domain/cattle';
import { createBatch, updateBatchStatus } from '../../stores/slices/cattle.slice';
import { AppDispatch } from '../../stores/store';

export const useBatchOperations = () => {
  const dispatch = useDispatch<AppDispatch>();
  const [operationLoading, setOperationLoading] = useState(false);
  const [operationError, setOperationError] = useState<string | null>(null);

  const createBatchWithStatus = async (batchData: BatchCreateRequest): Promise<Batch> => {
    setOperationLoading(true);
    setOperationError(null);
    try {
      const result = await dispatch(createBatch(batchData)).unwrap();
      return result;
    } catch (error: any) {
      const errorMessage = error.message || 'Failed to create batch';
      setOperationError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setOperationLoading(false);
    }
  };

  const updateBatchStatusWithStatus = async (batchId: number, statusData: any): Promise<any> => {
    setOperationLoading(true);
    setOperationError(null);
    try {
      const result = await dispatch(updateBatchStatus({ batchId, statusData })).unwrap();
      return result;
    } catch (error: any) {
      const errorMessage = error.message || 'Failed to update batch status';
      setOperationError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setOperationLoading(false);
    }
  };

  return {
    operationLoading,
    operationError,
    createBatch: createBatchWithStatus,
    updateBatchStatus: updateBatchStatusWithStatus,
    clearError: () => setOperationError(null)
  };
};