// src/hooks/cattle/useCattleStats.ts
import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchStats } from '../../stores/slices/cattle.slice';
import { AppDispatch } from '../../stores/store';
import { selectStats, selectLoading, selectError } from '../../stores/selectors/cattle.selectors';

export const useCattleStats = () => {
  const dispatch = useDispatch<AppDispatch>();
  
  // Usar selectores de Redux en lugar de estado local
  const stats = useSelector(selectStats);
  const loading = useSelector(selectLoading);
  const error = useSelector(selectError);

  const loadStats = async () => {
    try {
      await dispatch(fetchStats()).unwrap();
    } catch (error) {
      // El error ya está manejado por el slice de Redux
      console.error('Failed to load cattle stats:', error);
    }
  };

  useEffect(() => {
    loadStats();
  }, [dispatch]);

  const refreshStats = async () => {
    await loadStats();
  };

  return {
    stats,
    loading,
    error,
    refreshStats,
    clearError: () => {} // Los errores se limpian automáticamente en el slice
  };
};