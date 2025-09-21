// src/stores/store.ts (actualización)
import { configureStore } from '@reduxjs/toolkit';
import cattleReducer from './slices/cattle.slice';
// ... otros reducers

export const store = configureStore({
  reducer: {
    cattle: cattleReducer,
    // ... otros reducers
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;