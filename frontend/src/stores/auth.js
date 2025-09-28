import { defineStore } from 'pinia';
import { jwtDecode } from 'jwt-decode'; // <-- Importar el decodificador
import apiClient from '../services/api';
import router from '../router';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: localStorage.getItem('accessToken') || null,
    refreshToken: localStorage.getItem('refreshToken') || null,
    user: JSON.parse(localStorage.getItem('user')) || null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.accessToken,
  },
  actions: {
    // --- Acción para manejar el guardado de la sesión ---
    _setSession(access, refresh = null) {
      this.accessToken = access;
      localStorage.setItem('accessToken', access);

      if (refresh) {
        this.refreshToken = refresh;
        localStorage.setItem('refreshToken', refresh);
      }

      // Decodificar el token para obtener datos del usuario
      const decoded = jwtDecode(access);
      this.user = {
        email: decoded.email,
        first_name: decoded.first_name,
      };
      localStorage.setItem('user', JSON.stringify(this.user));
    },

    // --- Acción de Login ---
    async login(credentials) {
      const response = await apiClient.post('/auth/login/', credentials);
      const { access, refresh } = response.data;
      this._setSession(access, refresh);
      router.push({ name: 'Dashboard' });
    },

    // --- Acción de Registro (Refactorizada) ---
    async register(payload) {
      const response = await apiClient.post('/auth/register/', payload);
      const { access, refresh } = response.data;
      // El endpoint de registro devuelve el usuario, pero lo estandarizamos
      this._setSession(access, refresh);
      router.push({ name: 'Dashboard' });
    },

    // --- NUEVA ACCIÓN DE REFRESCAR TOKEN ---
    async refreshToken() {
      if (!this.refreshToken) {
        throw new Error("No hay refresh token disponible.");
      }
      try {
        const response = await apiClient.post('/auth/login/refresh/', {
          refresh: this.refreshToken,
        });
        const { access } = response.data;
        this._setSession(access); // Actualiza solo el access token
        return access;
      } catch (error) {
        // Si el refresco falla, la sesión es irrecuperable.
        // Forzamos un logout completo.
        await this.logout();
        throw error;
      }
    },

   async logout() {
      if (this.refreshToken) {
        try {
          await apiClient.post('/auth/logout/', {
            refresh: this.refreshToken,
          });
        } catch (error) {
          console.error("Fallo en el endpoint de logout (puede que el token ya fuera inválido). Se procederá a limpiar la sesión local.", error);
        }
      }

      // Limpieza final del estado y localStorage
      this.accessToken = null;
      this.refreshToken = null;
      this.user = null;
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('user');

      // Aseguramos que la redirección no cause problemas si el router no está listo
      if (router.currentRoute.value.name !== 'Login') {
        router.push({ name: 'Login' });
      }
    },
  },
});