// src/hooks/cattle/useBatchOperations.ts
import { useState } from 'react';
import { useCattle } from './useCattle';
import { Batch, BatchCreateRequest } from '../../types/domain/cattle';

export const useBatchOperations = () => {
  const cattle = useCattle();
  const [operationLoading, setOperationLoading] = useState(false);
  const [operationError, setOperationError] = useState<string | null>(null);

  const createBatchWithStatus = async (batchData: BatchCreateRequest): Promise<Batch> => {
    setOperationLoading(true);
    setOperationError(null);
    try {
      const newBatch = await cattle.createBatch(batchData);
      return newBatch;
    } catch (error) {
      setOperationError(cattle.error);
      throw error;
    } finally {
      setOperationLoading(false);
    }
  };

  const updateBatchStatusWithStatus = async (batchId: number, statusData: any): Promise<any> => {
    setOperationLoading(true);
    setOperationError(null);
    try {
      const result = await cattle.updateBatchStatus(batchId, statusData);
      return result;
    } catch (error) {
      setOperationError(cattle.error);
      throw error;
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