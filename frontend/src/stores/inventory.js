import { defineStore } from 'pinia';
import apiClient from '../services/api';

export const useInventoryStore = defineStore('inventory', {
  state: () => ({
    _rawMaterials: [],
    pagination: { count: 0, page: 1, totalPages: 1 },
    selectedRawMaterial: null,
    purchaseBatches: [],
    isLoadingList: false,
    isLoadingDetail: false,
    isLoadingBatches: false,
    error: null,
    _unitsOfMeasure: [],
    ordering: '',
    unitOfMeasureFilter: '',
    batchesPagination: { count: 0, page: 1, totalPages: 1 },
    batchesOrdering: '-purchase_date',
  }),
  getters: {
    rawMaterials: (state) => state._rawMaterials,
    unitsOfMeasure: (state) => ['Todos', ...(state._unitsOfMeasure || [])],
  },
  actions: {
    // --- ACCIONES DE MATERIAS PRIMAS ---
    async fetchRawMaterials(page = 1, searchTerm = '') {
      this.isLoadingList = true;
      this.error = null;
      const params = new URLSearchParams();
      params.append('page', page);
      if (searchTerm.trim()) { params.append('search', searchTerm.trim()); }
      if (this.ordering) { params.append('ordering', this.ordering); }
      if (this.unitOfMeasureFilter) { params.append('unit_of_measure', this.unitOfMeasureFilter); }
      try {
        const response = await apiClient.get(`/inventory/raw-materials/?${params.toString()}`);
        this._rawMaterials = response.data.results;
        this.pagination.count = response.data.count;
        this.pagination.page = page;
        this.pagination.totalPages = Math.ceil(response.data.count / 6);
      } catch (error) {
        console.error("Error al obtener materias primas:", error);
        this.error = "No se pudieron cargar las materias primas.";
        this._rawMaterials = [];
      } finally {
        this.isLoadingList = false;
      }
    },
    async fetchUnitsOfMeasure() {
      try {
        if (this._unitsOfMeasure.length > 0) return;
        const response = await apiClient.get('/inventory/raw-materials/units/');
        this._unitsOfMeasure = response.data;
      } catch (error) {
        console.error("Error al obtener unidades de medida:", error);
        this._unitsOfMeasure = [];
      }
    },
    setOrdering(columnKey) {
      if (this.ordering === columnKey) { this.ordering = `-${columnKey}`; }
      else if (this.ordering === `-${columnKey}`) { this.ordering = ''; }
      else { this.ordering = columnKey; }
      this.fetchRawMaterials(1, '');
    },
    setUnitOfMeasureFilter(unit) {
      this.unitOfMeasureFilter = unit === 'Todos' ? '' : unit;
      this.fetchRawMaterials(1, '');
    },
    async fetchRawMaterialById(id) {
        this.isLoadingDetail = true;
        this.error = null;
        this.selectedRawMaterial = null;
        try {
            const response = await apiClient.get(`/inventory/raw-materials/${id}/`);
            this.selectedRawMaterial = response.data;
        } catch (error) {
            console.error(`Error al obtener materia prima ${id}:`, error);
            this.error = "No se pudo cargar la materia prima seleccionada.";
        } finally {
            this.isLoadingDetail = false;
        }
    },
    clearDetailState() {
        this.selectedRawMaterial = null;
        this.purchaseBatches = [];
        this.error = null;
        this.batchesPagination = { count: 0, page: 1, totalPages: 1 };
        this.batchesOrdering = '-purchase_date';
    },

    // --- ACCIÓN DE CREACIÓN (REDISEÑADA) ---
    async createRawMaterial(payload) {
      try {
        await apiClient.post('/inventory/raw-materials/', payload);
        // GARANTÍA DE CONSISTENCIA: Volvemos a pedir la primera página para tener los datos más frescos.
        await this.fetchRawMaterials(1, '');
      } catch (error) {
        console.error("Error al crear materia prima:", error);
        throw error;
      }
    },

    // --- ACCIÓN DE ACTUALIZACIÓN (REDISEÑADA) ---
    async updateRawMaterial(id, payload) {
      try {
        await apiClient.put(`/inventory/raw-materials/${id}/`, payload);
        // GARANTÍA DE CONSISTENCIA: Volvemos a pedir la página actual para refrescar los datos.
        await this.fetchRawMaterials(this.pagination.page, '');
      } catch (error) {
        console.error("Error al actualizar materia prima:", error);
        throw error;
      }
    },

    async deleteRawMaterial(id, currentSearchTerm) {
      try {
        await apiClient.delete(`/inventory/raw-materials/${id}/`);
        if (this._rawMaterials.length === 1 && this.pagination.page > 1) {
          await this.fetchRawMaterials(this.pagination.page - 1, currentSearchTerm);
        } else {
          await this.fetchRawMaterials(this.pagination.page, currentSearchTerm);
        }
      } catch (error) {
        console.error("Error al eliminar materia prima:", error);
        throw error;
      }
    },

    // --- ACCIONES DE LOTES DE COMPRA ---
    async fetchPurchaseBatches(materialId, page = 1) {
      this.isLoadingBatches = true;
      this.error = null;
      const params = new URLSearchParams();
      params.append('material_id', materialId);
      params.append('page', page);
      if (this.batchesOrdering) {
        params.append('ordering', this.batchesOrdering);
      }
      try {
        const response = await apiClient.get(`/inventory/purchase-batches/?${params.toString()}`);
        if (response.data && Array.isArray(response.data.results)) {
          this.purchaseBatches = response.data.results;
          this.batchesPagination.count = response.data.count;
          this.batchesPagination.page = page;
          this.batchesPagination.totalPages = Math.ceil(response.data.count / 6);
        } else if (Array.isArray(response.data)) {
          this.purchaseBatches = response.data;
        }
      } catch (error) {
        console.error(`Error al obtener lotes para materia prima ${materialId}:`, error);
        this.error = "No se pudieron cargar los lotes de compra.";
      } finally {
        this.isLoadingBatches = false;
      }
    },
    setBatchesOrdering(materialId, columnKey) {
      if (this.batchesOrdering === columnKey) {
        this.batchesOrdering = `-${columnKey}`;
      } else if (this.batchesOrdering === `-${columnKey}`) {
        this.batchesOrdering = '';
      } else {
        this.batchesOrdering = columnKey;
      }
      this.fetchPurchaseBatches(materialId, 1);
    },

    // --- ACCIONES DE LOTES (REDISEÑADAS PARA CONSISTENCIA) ---
    async createPurchaseBatch(payload) {
        try {
            await apiClient.post('/inventory/purchase-batches/', payload);
            await this.fetchPurchaseBatches(payload.raw_material, 1);
            // También refrescamos el detalle de la materia prima para actualizar su stock total
            await this.fetchRawMaterialById(payload.raw_material);
        } catch (error) {
            console.error("Error al crear lote de compra:", error);
            throw error;
        }
    },
    async updatePurchaseBatch(id, payload) {
        try {
            await apiClient.put(`/inventory/purchase-batches/${id}/`, payload);
            await this.fetchPurchaseBatches(payload.raw_material, this.batchesPagination.page);
            await this.fetchRawMaterialById(payload.raw_material);
        } catch (error) {
            console.error(`Error al actualizar el lote ${id}:`, error);
            throw error;
        }
    },
    async deletePurchaseBatch(id, materialId) {
        try {
            await apiClient.delete(`/inventory/purchase-batches/${id}/`);
            await this.fetchPurchaseBatches(materialId, this.batchesPagination.page);
            await this.fetchRawMaterialById(materialId);
        } catch (error) {
            console.error(`Error al eliminar el lote ${id}:`, error);
            throw error;
        }
    },
  },
});