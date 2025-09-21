import { useCattleRedux } from './useCattleRedux';

// Hook unificado que usa Redux por detrás
export const useCattle = () => {
  return useCattleRedux();
};