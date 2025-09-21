// src/hooks/cattle/useAnimalOperations.ts
import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { Animal, AnimalCreateRequest, AnimalUpdateRequest } from '../../types/domain/cattle';
import { createAnimal, updateAnimal, deleteAnimal } from '../../stores/slices/cattle.slice';
import { AppDispatch } from '../../stores/store';

export const useAnimalOperations = () => {
  const dispatch = useDispatch<AppDispatch>();
  const [operationLoading, setOperationLoading] = useState(false);
  const [operationError, setOperationError] = useState<string | null>(null);

  const createAnimalWithStatus = async (animalData: AnimalCreateRequest): Promise<Animal> => {
    setOperationLoading(true);
    setOperationError(null);
    try {
      const result = await dispatch(createAnimal(animalData)).unwrap();
      return result;
    } catch (error: any) {
      const errorMessage = error.message || 'Failed to create animal';
      setOperationError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setOperationLoading(false);
    }
  };

  const updateAnimalWithStatus = async (id: number, animalData: AnimalUpdateRequest): Promise<Animal> => {
    setOperationLoading(true);
    setOperationError(null);
    try {
      const result = await dispatch(updateAnimal({ id, animalData })).unwrap();
      return result;
    } catch (error: any) {
      const errorMessage = error.message || 'Failed to update animal';
      setOperationError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setOperationLoading(false);
    }
  };

  const deleteAnimalWithStatus = async (id: number): Promise<void> => {
    setOperationLoading(true);
    setOperationError(null);
    try {
      await dispatch(deleteAnimal(id)).unwrap();
    } catch (error: any) {
      const errorMessage = error.message || 'Failed to delete animal';
      setOperationError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setOperationLoading(false);
    }
  };

  return {
    operationLoading,
    operationError,
    createAnimal: createAnimalWithStatus,
    updateAnimal: updateAnimalWithStatus,
    deleteAnimal: deleteAnimalWithStatus,
    clearError: () => setOperationError(null)
  };
};