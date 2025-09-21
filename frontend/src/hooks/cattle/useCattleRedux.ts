// frontend/src/hooks/cattle/useCattleRedux.ts
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
  selectBatch,
  // Añadir estos nuevos thunks
  fetchCertificationStandards,
  fetchAnimalCertifications,
  revokeCertification,
  fetchAnimalHealthRecords,
  mintAnimalNFT,
  transferAnimal,
  updateAnimalHealth,
  verifyAnimalNFT,
  getAnimalNFTInfo,
  getAnimalBlockchainEvents,
  getAnimalAuditTrail,
  updateBatchStatus,
  addAnimalsToBatch,
  removeAnimalsFromBatch,
  getBatchBlockchainEvents,
  getBatchAuditTrail,
  searchBatches,
  searchAnimals,
  exportAuditTrail
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
  selectAnimalsByHealth,
  selectCertifications,
  selectCertificationStandards
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
  const certifications = useSelector(selectCertifications);
  const certificationStandards = useSelector(selectCertificationStandards);

  // Acciones que devuelven promesas con los datos
  const getAnimals = useCallback(async (params?: any) => {
    const result = await dispatch(fetchAnimals(params)).unwrap();
    return result;
  }, [dispatch]);

  const getAnimal = useCallback(async (id: number) => {
    const result = await dispatch(fetchAnimal(id)).unwrap();
    return result;
  }, [dispatch]);

  const createAnimalAction = useCallback(async (animalData: any) => {
    const result = await dispatch(createAnimal(animalData)).unwrap();
    return result;
  }, [dispatch]);

  const updateAnimalAction = useCallback(async (id: number, animalData: any) => {
    const result = await dispatch(updateAnimal({ id, animalData })).unwrap();
    return result;
  }, [dispatch]);

  const deleteAnimalAction = useCallback(async (id: number) => {
    await dispatch(deleteAnimal(id)).unwrap();
  }, [dispatch]);

  const getBatches = useCallback(async (params?: any) => {
    const result = await dispatch(fetchBatches(params)).unwrap();
    return result;
  }, [dispatch]);

  const getBatch = useCallback(async (id: number) => {
    const result = await dispatch(fetchBatch(id)).unwrap();
    return result;
  }, [dispatch]);

  const createBatchAction = useCallback(async (batchData: any) => {
    const result = await dispatch(createBatch(batchData)).unwrap();
    return result;
  }, [dispatch]);

  const getStatsAction = useCallback(async () => {
    const result = await dispatch(fetchStats()).unwrap();
    return result;
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

  // Nuevas funciones que devuelven promesas
  const getCertificationStandards = useCallback(async () => {
    const result = await dispatch(fetchCertificationStandards()).unwrap();
    return result;
  }, [dispatch]);

  const getAnimalCertifications = useCallback(async (animalId: number) => {
    const result = await dispatch(fetchAnimalCertifications(animalId)).unwrap();
    return result;
  }, [dispatch]);

  const revokeCertificationAction = useCallback(async (certificationId: number, reason: string) => {
    const result = await dispatch(revokeCertification({ certificationId, reason })).unwrap();
    return result;
  }, [dispatch]);

  const getAnimalHealthRecords = useCallback(async (animalId: number) => {
    const result = await dispatch(fetchAnimalHealthRecords(animalId)).unwrap();
    return result;
  }, [dispatch]);

  const mintAnimalNFTAction = useCallback(async (animalId: number, mintData: any) => {
    const result = await dispatch(mintAnimalNFT({ animalId, mintData })).unwrap();
    return result;
  }, [dispatch]);

  const transferAnimalAction = useCallback(async (animalId: number, transferData: any) => {
    const result = await dispatch(transferAnimal({ animalId, transferData })).unwrap();
    return result;
  }, [dispatch]);

  const updateAnimalHealthAction = useCallback(async (animalId: number, healthData: any) => {
    const result = await dispatch(updateAnimalHealth({ animalId, healthData })).unwrap();
    return result;
  }, [dispatch]);

  const verifyAnimalNFTAction = useCallback(async (animalId: number) => {
    const result = await dispatch(verifyAnimalNFT(animalId)).unwrap();
    return result;
  }, [dispatch]);

  const getAnimalNFTInfoAction = useCallback(async (animalId: number) => {
    const result = await dispatch(getAnimalNFTInfo(animalId)).unwrap();
    return result;
  }, [dispatch]);

  const getAnimalBlockchainEventsAction = useCallback(async (animalId: number) => {
    const result = await dispatch(getAnimalBlockchainEvents(animalId)).unwrap();
    return result;
  }, [dispatch]);

  const getAnimalAuditTrailAction = useCallback(async (animalId: number) => {
    const result = await dispatch(getAnimalAuditTrail(animalId)).unwrap();
    return result;
  }, [dispatch]);

  const updateBatchStatusAction = useCallback(async (batchId: number, statusData: any) => {
    const result = await dispatch(updateBatchStatus({ batchId, statusData })).unwrap();
    return result;
  }, [dispatch]);

  const addAnimalsToBatchAction = useCallback(async (batchId: number, animalsData: any) => {
    const result = await dispatch(addAnimalsToBatch({ batchId, animalsData })).unwrap();
    return result;
  }, [dispatch]);

  const removeAnimalsFromBatchAction = useCallback(async (batchId: number, animalsData: any) => {
    const result = await dispatch(removeAnimalsFromBatch({ batchId, animalsData })).unwrap();
    return result;
  }, [dispatch]);

  const getBatchBlockchainEventsAction = useCallback(async (batchId: number) => {
    const result = await dispatch(getBatchBlockchainEvents(batchId)).unwrap();
    return result;
  }, [dispatch]);

  const getBatchAuditTrailAction = useCallback(async (batchId: number) => {
    const result = await dispatch(getBatchAuditTrail(batchId)).unwrap();
    return result;
  }, [dispatch]);

  const searchBatchesAction = useCallback(async (params: any) => {
    const result = await dispatch(searchBatches(params)).unwrap();
    return result;
  }, [dispatch]);

  const searchAnimalsAction = useCallback(async (params: any) => {
    const result = await dispatch(searchAnimals(params)).unwrap();
    return result;
  }, [dispatch]);

  const exportAuditTrailAction = useCallback(async (format?: 'json' | 'csv', days?: number) => {
    const result = await dispatch(exportAuditTrail({ format, days })).unwrap();
    return result;
  }, [dispatch]);

  return {
    // Estado
    animals,
    batches,
    certifications,
    certificationStandards,
    stats,
    selectedAnimal,
    selectedBatch,
    loading,
    error,
    
    // Acciones (ahora devuelven promesas con los datos)
    getAnimals,
    getAnimal,
    createAnimal: createAnimalAction,
    updateAnimal: updateAnimalAction,
    deleteAnimal: deleteAnimalAction,
    getBatches,
    getBatch,
    createBatch: createBatchAction,
    getStats: getStatsAction,
    clearError: clearCattleError,
    clearSelection: clearCattleSelection,
    selectAnimal: setSelectedAnimal,
    selectBatch: setSelectedBatch,
    
    // Nuevas acciones (devuelven promesas)
    getCertificationStandards,
    getAnimalCertifications,
    revokeCertification: revokeCertificationAction,
    getAnimalHealthRecords,
    mintAnimalNFT: mintAnimalNFTAction,
    transferAnimal: transferAnimalAction,
    updateAnimalHealth: updateAnimalHealthAction,
    verifyAnimalNFT: verifyAnimalNFTAction,
    getAnimalNFTInfo: getAnimalNFTInfoAction,
    getAnimalBlockchainEvents: getAnimalBlockchainEventsAction,
    getAnimalAuditTrail: getAnimalAuditTrailAction,
    updateBatchStatus: updateBatchStatusAction,
    addAnimalsToBatch: addAnimalsToBatchAction,
    removeAnimalsFromBatch: removeAnimalsFromBatchAction,
    getBatchBlockchainEvents: getBatchBlockchainEventsAction,
    getBatchAuditTrail: getBatchAuditTrailAction,
    searchBatches: searchBatchesAction,
    searchAnimals: searchAnimalsAction,
    exportAuditTrail: exportAuditTrailAction
  };
};

// Hook para selectores específicos (mantener igual)
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