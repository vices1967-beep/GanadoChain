// src/features/cattle/hooks/useCattleFilters.ts
import { useState, useMemo } from 'react';
import { Animal } from '../../../types/domain/cattle';

export const useCattleFilters = (animals: Animal[]) => {
  const [filters, setFilters] = useState({
    healthStatus: '',
    status: '',
    breed: '',
    search: ''
  });

  const filteredAnimals = useMemo(() => {
    return animals.filter(animal => {
      return (
        (filters.healthStatus === '' || animal.health_status === filters.healthStatus) &&
        (filters.status === '' || animal.status === filters.status) &&
        (filters.breed === '' || animal.breed.includes(filters.breed)) &&
        (filters.search === '' || 
          animal.ear_tag.toLowerCase().includes(filters.search.toLowerCase()) ||
          animal.name.toLowerCase().includes(filters.search.toLowerCase()) ||
          animal.location.toLowerCase().includes(filters.search.toLowerCase()))
      );
    });
  }, [animals, filters]);

  const updateFilter = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const clearFilters = () => {
    setFilters({
      healthStatus: '',
      status: '',
      breed: '',
      search: ''
    });
  };

  return {
    filters,
    filteredAnimals,
    updateFilter,
    clearFilters
  };
};