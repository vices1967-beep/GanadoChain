// src/hooks/cattle/useCattleRedux.ts
import { useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch, RootState } from '../../stores/store';
import {
  fetchAnimals,
  fetchAnimal,
  createAnimal,
  updateAnimal,
  deleteAnimal,
  fetchBatches,
  fetchBatch,
  createBatch,
  fetchStats,
  clearError,
  clearSelection,
  selectAnimal,
  selectBatch
} from '../../stores/slices/cattle.slice';
import {
  selectAnimals,
  selectAnimalById,
  selectBatches,
  selectBatchById,
  selectStats,
  selectSelectedAnimal,
  selectSelectedBatch,
  selectLoading,
  selectError,
  selectAnimalsByStatus,
  selectAnimalsByHealth
} from '../../stores/selectors/cattle.selectors';

export const useCattleRedux = () => {
  const dispatch = useDispatch<AppDispatch>();

  // Selectores
  const animals = useSelector(selectAnimals);
  const batches = useSelector(selectBatches);
  const stats = useSelector(selectStats);
  const selectedAnimal = useSelector(selectSelectedAnimal);
  const selectedBatch = useSelector(selectSelectedBatch);
  const loading = useSelector(selectLoading);
  const error = useSelector(selectError);

  // Acciones
  const getAnimals = useCallback((params?: any) => {
    return dispatch(fetchAnimals(params));
  }, [dispatch]);

  const getAnimal = useCallback((id: number) => {
    return dispatch(fetchAnimal(id));
  }, [dispatch]);

  const addAnimal = useCallback((animalData: any) => {
    return dispatch(createAnimal(animalData));
  }, [dispatch]);

  const modifyAnimal = useCallback((id: number, animalData: any) => {
    return dispatch(updateAnimal({ id, animalData }));
  }, [dispatch]);

  const removeAnimal = useCallback((id: number) => {
    return dispatch(deleteAnimal(id));
  }, [dispatch]);

  const getBatches = useCallback((params?: any) => {
    return dispatch(fetchBatches(params));
  }, [dispatch]);

  const getBatch = useCallback((id: number) => {
    return dispatch(fetchBatch(id));
  }, [dispatch]);

  const addBatch = useCallback((batchData: any) => {
    return dispatch(createBatch(batchData));
  }, [dispatch]);

  const getCattleStats = useCallback(() => {
    return dispatch(fetchStats());
  }, [dispatch]);

  const clearCattleError = useCallback(() => {
    dispatch(clearError());
  }, [dispatch]);

  const clearCattleSelection = useCallback(() => {
    dispatch(clearSelection());
  }, [dispatch]);

  const setSelectedAnimal = useCallback((animal: any) => {
    dispatch(selectAnimal(animal));
  }, [dispatch]);

  const setSelectedBatch = useCallback((batch: any) => {
    dispatch(selectBatch(batch));
  }, [dispatch]);

  return {
    // Estado
    animals,
    batches,
    stats,
    selectedAnimal,
    selectedBatch,
    loading,
    error,
    
    // Acciones
    getAnimals,
    getAnimal,
    createAnimal: addAnimal,
    updateAnimal: modifyAnimal,
    deleteAnimal: removeAnimal,
    getBatches,
    getBatch,
    createBatch: addBatch,
    getStats: getCattleStats,
    clearError: clearCattleError,
    clearSelection: clearCattleSelection,
    selectAnimal: setSelectedAnimal,
    selectBatch: setSelectedBatch
  };
};

// Hook para selectores específicos
export const useCattleSelectors = () => {
  const animalsByStatus = (status: string) => 
    useSelector((state: RootState) => selectAnimalsByStatus(state, status));
  
  const animalsByHealth = (healthStatus: string) => 
    useSelector((state: RootState) => selectAnimalsByHealth(state, healthStatus));
  
  const animalById = (id: number) => 
    useSelector((state: RootState) => selectAnimalById(state, id));
  
  const batchById = (id: number) => 
    useSelector((state: RootState) => selectBatchById(state, id));

  return {
    animalsByStatus,
    animalsByHealth,
    animalById,
    batchById
  };
};