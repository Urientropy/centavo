import axios from 'axios';
import { useAuthStore } from '../stores/auth';

// --- Función Auxiliar para leer Cookies ---
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
const csrftoken = getCookie('csrftoken');
// ------------------------------------

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  // --- INICIO: CORRECCIÓN CSRF ---
  // Permite que Axios envíe cookies cross-origin si fuera necesario
  // y es fundamental para que Django reciba el cookie de sesión.
  withCredentials: true,
  // --- FIN: CORRECCIÓN CSRF ---
});

apiClient.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore();
    const token = authStore.accessToken;
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }

    // --- INICIO: CORRECCIÓN CSRF ---
    // Añadimos el token CSRF a las cabeceras para peticiones 'mutantes'
    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(config.method.toUpperCase())) {
        if (csrftoken) {
            config.headers['X-CSRFToken'] = csrftoken;
        }
    }
    // --- FIN: CORRECCIÓN CSRF ---

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    const authStore = useAuthStore();
    const authEndpoints = ['/auth/login/', '/auth/login/refresh/', '/auth/logout/'];

    // Esta condición es crucial para producción, donde a veces no hay error.response
    if (!error.response || error.response.status !== 401 || originalRequest._retry) {
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