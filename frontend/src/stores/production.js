import { defineStore } from 'pinia';
import apiClient from '../services/api';

export const useProductionStore = defineStore('production', {
  state: () => ({
    productionLogs: [],
    pagination: { count: 0, page: 1, totalPages: 1 },
    isLoading: false,
    error: null,
    // --- INICIO: NUEVO ESTADO PARA FILTROS Y ORDEN ---
    ordering: '-production_date', // Por defecto, los más recientes primero
    searchTerm: '',
    // --- FIN: NUEVO ESTADO PARA FILTROS Y ORDEN ---
  }),
  actions: {
    async fetchProductionLogs(page = 1) {
      this.isLoading = true;
      this.error = null;
      const params = new URLSearchParams();
      params.append('page', page);
      if (this.searchTerm.trim()) { params.append('search', this.searchTerm.trim()); }
      if (this.ordering) { params.append('ordering', this.ordering); }

      try {
        const response = await apiClient.get(`/production-logs/?${params.toString()}`);
        this.productionLogs = response.data.results;
        this.pagination.count = response.data.count;
        this.pagination.page = page;
        this.pagination.totalPages = Math.ceil(response.data.count / 6);
      } catch (error) {
        console.error("Error al obtener los registros de producción:", error);
        this.error = "No se pudieron cargar los registros de producción.";
        this.productionLogs = [];
      } finally {
        this.isLoading = false;
      }
    },

    // --- INICIO: NUEVAS ACCIONES ---
    setOrdering(columnKey) {
      if (this.ordering === columnKey) { this.ordering = `-${columnKey}`; }
      else if (this.ordering === `-${columnKey}`) { this.ordering = ''; }
      else { this.ordering = columnKey; }
      this.fetchProductionLogs(1);
    },
    setSearchTerm(term) {
      this.searchTerm = term;
      this.fetchProductionLogs(1); // Siempre resetea a la página 1 al buscar
    },
    // --- FIN: NUEVAS ACCIONES ---

    async createProductionLog(payload) {
      this.error = null;
      try {
        await apiClient.post('/production-logs/', payload);
        await this.fetchProductionLogs(1);
        return { success: true };
      } catch (error) {
        console.error("Error al registrar la producción:", error);
        if (error.response && error.response.data) {
          this.error = error.response.data;
        } else {
          this.error = "Ocurrió un error inesperado en la red.";
        }
        throw error;
      }
    },
  },
});