// src/hooks/cattle/useAnimalOperations.ts
import { useState } from 'react';
import { useCattle } from './useCattle';
import { Animal, AnimalCreateRequest, AnimalUpdateRequest } from '../../types/domain/cattle';

export const useAnimalOperations = () => {
  const cattle = useCattle();
  const [operationLoading, setOperationLoading] = useState(false);
  const [operationError, setOperationError] = useState<string | null>(null);

  const createAnimalWithStatus = async (animalData: AnimalCreateRequest): Promise<Animal> => {
    setOperationLoading(true);
    setOperationError(null);
    try {
      const newAnimal = await cattle.createAnimal(animalData);
      return newAnimal;
    } catch (error) {
      setOperationError(cattle.error);
      throw error;
    } finally {
      setOperationLoading(false);
    }
  };

  const updateAnimalWithStatus = async (id: number, animalData: AnimalUpdateRequest): Promise<Animal> => {
    setOperationLoading(true);
    setOperationError(null);
    try {
      const updatedAnimal = await cattle.updateAnimal(id, animalData);
      return updatedAnimal;
    } catch (error) {
      setOperationError(cattle.error);
      throw error;
    } finally {
      setOperationLoading(false);
    }
  };

  const deleteAnimalWithStatus = async (id: number): Promise<void> => {
    setOperationLoading(true);
    setOperationError(null);
    try {
      await cattle.deleteAnimal(id);
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
    createAnimal: createAnimalWithStatus,
    updateAnimal: updateAnimalWithStatus,
    deleteAnimal: deleteAnimalWithStatus,
    clearError: () => setOperationError(null)
  };
};