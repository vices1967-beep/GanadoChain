// src/utils/errors.ts
export class ApiError extends Error {
  constructor(
    public message: string,
    public status?: number,
    public code?: string,
    public details?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export const handleApiError = (error: any): never => {
  if (error.response) {
    // El servidor respondió con un código de error
    const { status, data } = error.response;
    throw new ApiError(
      data.message || data.detail || 'Error del servidor',
      status,
      data.code,
      data.details
    );
  } else if (error.request) {
    // La request fue hecha pero no se recibió respuesta
    throw new ApiError('No se pudo conectar con el servidor');
  } else {
    // Error al configurar la request
    throw new ApiError(error.message || 'Error desconocido');
  }
};

export const isApiError = (error: any): error is ApiError => {
  return error instanceof ApiError;
};

export const getErrorMessage = (error: any): string => {
  if (isApiError(error)) {
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'Error desconocido';
};