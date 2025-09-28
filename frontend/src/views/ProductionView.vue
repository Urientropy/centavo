<template>
  <div>
    <h1 class="font-display text-4xl font-extrabold text-gray-graphite mb-8">Registros de Producción</h1>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">

      <div class="lg:col-span-1">
        <div class="bg-white p-6 rounded-lg border-2 border-gray-graphite shadow-[8px_8px_0px_#1F2937] sticky top-8">
          <h2 class="font-display text-2xl font-bold text-gray-graphite mb-4">Registrar Nueva Producción</h2>

          <form @submit.prevent="handleProductionSubmit">
            <div class="space-y-4">
              <div>
                <label for="product" class="block font-bold text-gray-graphite mb-1">Producto Terminado</label>
                <select id="product" v-model="form.product_id" required class="w-full px-4 py-2 border-2 border-gray-graphite rounded-md focus:ring-2 focus:ring-cyan-energetic focus:outline-none transition bg-white">
                  <option disabled value="">Seleccione un producto</option>
                  <option v-for="product in productList" :key="product.id" :value="product.id">{{ product.name }}</option>
                </select>
              </div>
              <div>
                <label for="quantity" class="block font-bold text-gray-graphite mb-1">Cantidad a Producir</label>
                <input id="quantity" type="number" v-model="form.quantity_produced" required min="0.01" step="0.01" placeholder="Ej: 15.50" class="w-full px-4 py-2 border-2 border-gray-graphite rounded-md focus:ring-2 focus:ring-cyan-energetic focus:outline-none transition" />
              </div>
            </div>

            <div v-if="error" class="mt-4 p-3 rounded-md bg-magenta-vibrant/10 text-magenta-vibrant border border-magenta-vibrant/20 text-sm">
              <p class="font-bold mb-1">Error al registrar la producción:</p>
              <p v-if="error.error_code === 'INSUFFICIENT_STOCK'">Se necesitan <strong class="font-extrabold">{{ error.quantity_required }}</strong> de <strong class="font-extrabold">{{ error.missing_raw_material.name }}</strong>, pero solo hay <strong class="font-extrabold">{{ error.quantity_available }}</strong> disponibles.</p>
              <p velse>{{ error.detail || 'Ha ocurrido un error inesperado.' }}</p>
            </div>

            <div class="mt-6">
              <button type="submit" :disabled="isSubmitting" class="w-full font-bold bg-cyan-energetic text-white py-2 px-6 rounded-md border-2 border-gray-graphite shadow-[4px_4px_0px_#1F2937] hover:shadow-[2px_2px_0px_#1F2937] active:translate-x-[2px] active:translate-y-[2px] active:shadow-none transition-all disabled:bg-gray-400 disabled:shadow-none disabled:cursor-not-allowed">
                <span v-if="isSubmitting">Registrando...</span>
                <span v-else>Confirmar Producción</span>
              </button>
            </div>
          </form>
        </div>
      </div>

      <div class="lg:col-span-2">
        <div class="mb-6">
          <input
            type="text"
            v-model="searchQuery"
            placeholder="Buscar por nombre de producto..."
            class="w-full max-w-sm px-4 py-2 border-2 border-gray-graphite rounded-md focus:ring-2 focus:ring-cyan-energetic focus:outline-none transition"
          />
        </div>

        <DataTable
          :columns="tableColumns"
          :items="productionLogs"
          :is-loading="isLoading"
          :pagination="pagination"
          :current-sort="currentSortState"
          @change-page="handleChangePage"
          @sort-change="handleSortChange"
        >
          <template #cell(total_cost)="{ item }">
            <span class="font-bold text-gray-graphite">C${{ parseFloat(item.total_cost).toFixed(2) }}</span>
          </template>
          <template #cell(production_date)="{ item }">
            <span>{{ format(new Date(item.production_date), 'dd MMM yyyy, h:mm a') }}</span>
          </template>
        </DataTable>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed, watch } from 'vue';
import { useProductionStore } from '../stores/production';
import { useProductStore } from '../stores/product';
import { useInventoryStore } from '../stores/inventory';
import { storeToRefs } from 'pinia';
import DataTable from '../components/DataTable.vue';
import { format } from 'date-fns';

const productionStore = useProductionStore();
const { productionLogs, isLoading, error, pagination, ordering } = storeToRefs(productionStore);
const productStore = useProductStore();
const { products: productList } = storeToRefs(productStore);
const inventoryStore = useInventoryStore();
const isSubmitting = ref(false);
const form = ref({ product_id: '', quantity_produced: '' });
const searchQuery = ref('');
let debounceTimer = null;

const tableColumns = [
  { key: 'product_name', label: 'Producto Fabricado' },
  { key: 'quantity_produced', label: 'Cantidad Producida' },
  { key: 'total_cost', label: 'Costo de Producción' },
  { key: 'production_date', label: 'Fecha', sortable: true },
];

const currentSortState = computed(() => {
  if (ordering.value.startsWith('-')) { return { key: ordering.value.substring(1), direction: 'desc' }; }
  if (ordering.value) { return { key: ordering.value, direction: 'asc' }; }
  return { key: '', direction: '' };
});

watch(searchQuery, (newQuery) => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    productionStore.setSearchTerm(newQuery);
  }, 300);
});

const handleProductionSubmit = async () => {
  isSubmitting.value = true;
  try {
    const result = await productionStore.createProductionLog(form.value);
    if (result.success) {
      form.value.product_id = '';
      form.value.quantity_produced = '';
      productionStore.error = null;
      await inventoryStore.fetchRawMaterials(1);
      await productStore.fetchProducts();
    }
  } catch (e) {
    console.log("La operación de producción falló, el error se mostrará en la UI.");
  } finally {
    isSubmitting.value = false;
  }
};
const handleChangePage = (newPage) => { productionStore.fetchProductionLogs(newPage); };
const handleSortChange = (columnKey) => { productionStore.setOrdering(columnKey); };

onMounted(() => {
  productionStore.fetchProductionLogs();
  if (productList.value.length === 0) {
    productStore.fetchProducts();
  }
});
</script>