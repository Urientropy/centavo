import { defineStore } from 'pinia';
import apiClient from '../services/api';

export const useProductStore = defineStore('product', {
  state: () => ({
    products: [],
    pagination: { count: 0, page: 1, totalPages: 1 },
    isLoading: false,
    error: null,
    _categories: [],
    categoryFilter: '',
    ordering: '',
    selectedProduct: null,
    isLoadingDetail: false,
    // --- INICIO: NUEVO ESTADO PARA DATOS DEL GRÁFICO ---
    stockEvolutionData: null, // { labels: [], data: [] }
    // --- FIN: NUEVO ESTADO PARA DATOS DEL GRÁFICO ---
  }),
  getters: {
    categories: (state) => ['Todas', ...(state._categories || [])],
  },
  actions: {
    async fetchProducts(page = 1, searchTerm = '') {
      this.isLoading = true;
      this.error = null;
      const params = new URLSearchParams();
      params.append('page', page);
      if (searchTerm.trim()) { params.append('search', searchTerm.trim()); }
      if (this.ordering) { params.append('ordering', this.ordering); }
      if (this.categoryFilter) { params.append('category', this.categoryFilter); }

      try {
        const response = await apiClient.get(`/products/?${params.toString()}`);
        this.products = response.data.results;
        this.pagination.count = response.data.count;
        this.pagination.page = page;
        this.pagination.totalPages = Math.ceil(response.data.count / 6);
      } catch (error) {
        console.error("Error al obtener productos:", error);
        this.error = "No se pudieron cargar los productos.";
        this.products = [];
      } finally {
        this.isLoading = false;
      }
    },

    async fetchCategories() {
      try {
        if (this._categories.length > 0) return;
        const response = await apiClient.get('/products/categories/');
        this._categories = response.data;
      } catch (error) {
        console.error("Error al obtener categorías:", error);
        this._categories = [];
      }
    },

    async fetchProductById(id) {
      this.isLoadingDetail = true;
      this.error = null;
      this.selectedProduct = null;
      try {
        const response = await apiClient.get(`/products/${id}/`);
        this.selectedProduct = response.data;
      } catch (error) {
        console.error(`Error al obtener el producto ${id}:`, error);
        this.error = "No se pudo cargar el producto seleccionado.";
      } finally {
        this.isLoadingDetail = false;
      }
    },

    // --- INICIO: NUEVA ACCIÓN PARA EL GRÁFICO ---
    async fetchStockEvolution(productId) {
      this.stockEvolutionData = null; // Resetea antes de la nueva llamada
      try {
        const response = await apiClient.get(`/products/${productId}/stock_evolution/`);
        this.stockEvolutionData = response.data;
      } catch (error) {
        console.error(`Error al obtener el historial de stock para el producto ${productId}:`, error);
        // Dejamos el estado en null para indicar que la carga falló.
        // No se considera un error crítico para mostrar al usuario.
      }
    },
    // --- FIN: NUEVA ACCIÓN PARA EL GRÁFICO ---

    clearDetailState() {
      this.selectedProduct = null;
      this.error = null;
      this.stockEvolutionData = null; // Limpiar datos del gráfico
    },

    setOrdering(columnKey) {
      if (this.ordering === columnKey) { this.ordering = `-${columnKey}`; }
      else if (this.ordering === `-${columnKey}`) { this.ordering = ''; }
      else { this.ordering = columnKey; }
      this.fetchProducts(1);
    },

    setCategoryFilter(category) {
      this.categoryFilter = category === 'Todas' ? '' : category;
      this.fetchProducts(1);
    },

    async createProduct(payload) {
      try {
        await apiClient.post('/products/', payload);
        await this.fetchProducts(1);
      } catch (error) {
        console.error("Error al crear el producto:", error);
        throw error;
      }
    },

    async updateProduct(id, payload, context = 'list') {
      try {
        await apiClient.patch(`/products/${id}/`, payload);
        if (context === 'detail') {
          await this.fetchProductById(id);
        } else {
          await this.fetchProducts(this.pagination.page);
        }
      } catch (error) {
        console.error(`Error al actualizar el producto ${id}:`, error);
        if (error.response) {
            console.error('Detalles del error:', error.response.data);
        }
        throw error;
      }
    },

    async deleteProduct(id) {
      try {
        await apiClient.delete(`/products/${id}/`);
        if (this.products.length === 1 && this.pagination.page > 1) {
          await this.fetchProducts(this.pagination.page - 1);
        } else {
          await this.fetchProducts(this.pagination.page);
        }
      } catch (error) {
        console.error(`Error al eliminar el producto ${id}:`, error);
        this.error = "No se pudo eliminar el producto.";
        throw error;
      }
    }
  },
});