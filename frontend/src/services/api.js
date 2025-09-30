import axios from 'axios';
import { useAuthStore } from '../stores/auth';

const apiClient = axios.create({
  // --- INICIO: CAMBIO CRÍTICO ---
  // Leemos la URL base de la API desde las variables de entorno de Vite.
  // En desarrollo, será 'http://localhost:8000/api/v1'.
  // En producción, será '/api/v1'.
  baseURL: import.meta.env.VITE_API_BASE_URL,
  // --- FIN: CAMBIO CRÍTICO ---
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

// --- Interceptor de Respuesta (Sin cambios) ---
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    const authStore = useAuthStore();

    const authEndpoints = [
      '/auth/login/',
      '/auth/login/refresh/',
      '/auth/logout/'
    ];

    if (error.response.status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }

    if (authEndpoints.some(endpoint => originalRequest.url.includes(endpoint))) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    try {
      const newAccessToken = await authStore.refreshToken();
      originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
      return apiClient(originalRequest);
    } catch (refreshError) {
      return Promise.reject(refreshError);
    }
  }
);

export default apiClient;