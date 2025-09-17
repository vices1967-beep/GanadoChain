// src/hooks/cattle/useCattleStats.ts
import { useState, useEffect } from 'react';
import { useCattle } from './useCattle';
import { CattleStats } from '../../types/domain/cattle';

export const useCattleStats = () => {
  const cattle = useCattle();
  const [stats, setStats] = useState<CattleStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const statsData = await cattle.getStats();
      setStats(statsData);
    } catch (err) {
      setError(cattle.error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  const refreshStats = async () => {
    await loadStats();
  };

  return {
    stats,
    loading,
    error,
    refreshStats,
    clearError: () => setError(null)
  };
};