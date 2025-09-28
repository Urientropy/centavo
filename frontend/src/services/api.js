import axios from 'axios';
import { useAuthStore } from '../stores/auth';

const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- Interceptor de Petición (Sin cambios) ---
apiClient.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore();
    const token = authStore.accessToken;
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// --- Interceptor de Respuesta (COMPLETAMENTE REFACTORIZADO) ---
apiClient.interceptors.response.use(
  (response) => {
    // Si la respuesta es exitosa, no hacemos nada.
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    const authStore = useAuthStore();

    // Lista de endpoints que no deben activar la lógica de refresco.
    const authEndpoints = [
      '/auth/login/',
      '/auth/login/refresh/',
      '/auth/logout/'
    ];

    // Condición 1: El error no es un 401, o ya es un reintento. No hacemos nada.
    if (error.response.status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }

    // Condición 2: El error es 401, PERO viene de un endpoint de autenticación.
    // Esto previene el bucle infinito. Dejamos que el error se propague al .catch() del componente.
    if (authEndpoints.some(endpoint => originalRequest.url.includes(endpoint))) {
      return Promise.reject(error);
    }

    // Si llegamos aquí, es un 401 de una ruta protegida. Intentamos refrescar el token.
    originalRequest._retry = true;

    try {
      const newAccessToken = await authStore.refreshToken();

      // Reintentamos la petición original con el nuevo token.
      originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
      return apiClient(originalRequest);
    } catch (refreshError) {
      // Si el refresco falla, el store de Pinia ya se encarga del logout.
      // Simplemente propagamos el error del refresco.
      return Promise.reject(refreshError);
    }
  }
);

export default apiClient;