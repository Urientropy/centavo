<template>
  <div>
    <div v-if="isLoadingInitialData" class="text-center p-12">
      <p class="font-display font-bold text-xl text-gray-graphite">Cargando productos...</p>
    </div>

    <div v-else>
      <div class="flex flex-col md:flex-row md:justify-between md:items-center mb-8 gap-4">
        <h1 class="font-display text-4xl font-extrabold text-gray-graphite">Productos Terminados</h1>
        <button
          @click="openCreateModal"
          class="font-bold bg-cyan-energetic text-white py-2 px-6 rounded-md border-2 border-gray-graphite shadow-[4px_4px_0px_#1F2937] hover:shadow-[2px_2px_0px_#1F2937] active:translate-x-[2px] active:translate-y-[2px] active:shadow-none transition-all self-start md:self-center">
          + Añadir Producto
        </button>
      </div>

      <div class="flex flex-col md:flex-row gap-4 mb-6">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Buscar producto..."
          class="w-full md:max-w-sm px-4 py-2 border-2 border-gray-graphite rounded-md focus:ring-2 focus:ring-cyan-energetic focus:outline-none transition"
        />
        <select
          v-model="selectedCategory"
          @change="handleCategoryFilterChange"
          class="w-full md:w-auto px-4 py-2 border-2 border-gray-graphite rounded-md focus:ring-2 focus:ring-cyan-energetic focus:outline-none transition bg-white"
        >
          <option v-for="cat in categories" :key="cat" :value="cat">
            {{ cat === 'Todas' ? 'Todas las categorías' : cat }}
          </option>
        </select>
      </div>

      <div>
        <div v-if="error" class="bg-magenta-vibrant/10 text-magenta-vibrant font-bold p-4 rounded-md text-center mb-8">
          {{ error }}
        </div>

        <DataTable
          :columns="tableColumns"
          :items="products"
          :is-loading="isLoading"
          :pagination="pagination"
          :current-sort="currentSortState"
          @change-page="handleChangePage"
          @sort-change="handleSortChange"
        >
          <template #cell(name)="{ item }">
            <router-link
              :to="{ name: 'ProductDetail', params: { id: item.id } }"
              class="font-bold text-indigo-electric hover:underline"
            >
              {{ item.name }}
            </router-link>
          </template>
          <template #cell(sale_price)="{ item }">
            <span class="font-bold text-gray-graphite">C${{ parseFloat(item.sale_price).toFixed(2) }}</span>
          </template>
          <template #cell(stock)="{ item }">
            <span class="font-bold">{{ item.stock }}</span>
          </template>
          <template #cell(actions)="{ item }">
            <div class="flex justify-end items-center space-x-4">
              <button @click="openEditModal(item)" class="font-bold text-indigo-electric hover:underline">Editar</button>
              <button @click="openDeleteModal(item)" class="font-bold text-magenta-vibrant hover:underline">Eliminar</button>
            </div>
          </template>
        </DataTable>
      </div>

      <Modal :show="isFormModalOpen" @close="closeFormModal" :title="modalTitle">
        <ProductForm :initial-data="selectedProduct" @close="closeFormModal" />
      </Modal>

      <ConfirmationModal v-if="productToDelete" :show="isDeleteModalOpen" title="Confirmar Eliminación" confirm-text="Sí, Eliminar" @close="closeDeleteModal" @confirm="confirmDelete">
        <p class="text-gray-graphite">
          ¿Estás seguro de que quieres eliminar el producto
          <strong class="font-bold text-magenta-vibrant">"{{ productToDelete.name }}"</strong>?
          Esta acción no se puede deshacer.
        </p>
      </ConfirmationModal>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed, watch } from 'vue';
import { useProductStore } from '../stores/product';
import { storeToRefs } from 'pinia';
import DataTable from '../components/DataTable.vue';
import Modal from '../components/Modal.vue';
import ProductForm from '../components/ProductForm.vue';
import ConfirmationModal from '../components/ConfirmationModal.vue';

const productStore = useProductStore();
const { products, isLoading, error, pagination, categories, ordering } = storeToRefs(productStore);
const isLoadingInitialData = ref(true);
const isFormModalOpen = ref(false);
const selectedProduct = ref(null);
const modalTitle = computed(() => selectedProduct.value ? 'Editar Producto' : 'Añadir Nuevo Producto');
const isDeleteModalOpen = ref(false);
const productToDelete = ref(null);
const searchQuery = ref('');
const selectedCategory = ref('Todas');
let debounceTimer = null;

const tableColumns = [
  { key: 'name', label: 'Nombre', sortable: true },
  { key: 'category', label: 'Categoría', sortable: true },
  { key: 'sale_price', label: 'Precio de Venta', sortable: true },
  { key: 'stock', label: 'Stock Actual', sortable: true },
  { key: 'actions', label: 'Acciones', headerClass: 'text-right', cellClass: 'text-right w-px whitespace-nowrap' },
];

const currentSortState = computed(() => {
  if (ordering.value.startsWith('-')) { return { key: ordering.value.substring(1), direction: 'desc' }; }
  if (ordering.value) { return { key: ordering.value, direction: 'asc' }; }
  return { key: '', direction: '' };
});

watch(searchQuery, (newQuery) => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    productStore.fetchProducts(1, newQuery);
  }, 300);
});

const handleChangePage = (newPage) => { productStore.fetchProducts(newPage, searchQuery.value); };
const handleSortChange = (columnKey) => { searchQuery.value = ''; productStore.setOrdering(columnKey); };
const handleCategoryFilterChange = () => { searchQuery.value = ''; productStore.setCategoryFilter(selectedCategory.value); };
const openCreateModal = () => { selectedProduct.value = null; isFormModalOpen.value = true; };
const openEditModal = (product) => { selectedProduct.value = { ...product }; isFormModalOpen.value = true; };
const closeFormModal = () => { isFormModalOpen.value = false; selectedProduct.value = null; };
const openDeleteModal = (product) => { productToDelete.value = product; isDeleteModalOpen.value = true; };
const closeDeleteModal = () => { isDeleteModalOpen.value = false; setTimeout(() => { productToDelete.value = null; }, 300); };
const confirmDelete = async () => { if (productToDelete.value) { productStore.deleteProduct(productToDelete.value.id); closeDeleteModal(); } };

onMounted(async () => {
  try {
    await Promise.all([
      productStore.fetchProducts(),
      productStore.fetchCategories()
    ]);
  } catch(e) {
    console.error("Fallo durante el montaje inicial de Productos:", e);
  } finally {
    isLoadingInitialData.value = false;
  }
});
</script>