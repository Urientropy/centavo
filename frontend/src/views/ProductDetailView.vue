<template>
  <div>
    <router-link :to="{ name: 'Products' }" class="inline-flex items-center gap-2 font-bold text-indigo-electric hover:underline mb-6 group">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5 transition-transform group-hover:-translate-x-1">
        <path fill-rule="evenodd" d="M17 10a.75.75 0 01-.75.75H5.612l4.158 3.96a.75.75 0 11-1.04 1.08l-5.5-5.25a.75.75 0 010-1.08l5.5-5.25a.75.75 0 111.04 1.08L5.612 9.25H16.25A.75.75 0 0117 10z" clip-rule="evenodd" />
      </svg>
      Volver a Productos
    </router-link>

    <div v-if="isLoadingDetail" class="text-center p-12">
      <p class="font-bold font-display text-xl">Cargando detalles del producto...</p>
    </div>
    <div v-else-if="error && !selectedProduct" class="bg-magenta-vibrant/10 text-magenta-vibrant font-bold p-4 rounded-md text-center">
      <p>{{ error }}</p>
    </div>

    <div v-else-if="selectedProduct" class="grid grid-cols-1 lg:grid-cols-3 gap-8">

      <div class="lg:col-span-2 flex flex-col gap-8">
        <article class="bg-white p-6 md:p-8 rounded-lg border-2 border-gray-graphite shadow-[8px_8px_0px_#1F2937]">
          <span class="font-display font-bold text-gray-graphite/60">{{ selectedProduct.category }}</span>
          <h1 class="font-display text-4xl lg:text-5xl font-extrabold text-gray-graphite mt-1">{{ selectedProduct.name }}</h1>
          <p class="mt-4 text-lg text-gray-graphite/80">{{ selectedProduct.description || 'Sin descripción detallada.' }}</p>
        </article>

        <article class="bg-white p-6 md:p-8 rounded-lg border-2 border-gray-graphite shadow-[8px_8px_0px_#1F2937]">
          <div class="flex justify-between items-center mb-4">
            <h2 class="font-display text-3xl font-extrabold text-gray-graphite">Receta / Ingredientes</h2>
            <button @click="isRecipeModalOpen = true" class="font-bold bg-indigo-electric text-white py-2 px-4 rounded-md border-2 border-gray-graphite shadow-[2px_2px_0px_#1F2937] hover:shadow-[1px_1px_0px_#1F2937] active:translate-x-[1px] active:translate-y-[1px] active:shadow-none transition-all text-sm">
              Gestionar Receta
            </button>
          </div>

          <div v-if="!selectedProduct.recipe_ingredients || selectedProduct.recipe_ingredients.length === 0" class="mt-4 text-center border-2 border-dashed border-gray-400 p-12 rounded-lg">
            <h3 class="font-display font-bold text-xl text-gray-graphite">Receta Vacía</h3>
            <p class="text-gray-graphite/80 mt-2">Este producto aún no tiene ingredientes asignados.</p>
          </div>

          <div v-else class="overflow-x-auto mt-4">
            <table class="w-full">
              <thead class="border-b-2 border-gray-graphite">
                <tr>
                  <th class="text-left p-2 font-display font-bold">Ingrediente</th>
                  <th class="text-right p-2 font-display font-bold">Cantidad</th>
                  <th class="text-right p-2 font-display font-bold">Unidad</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="ing in selectedProduct.recipe_ingredients" :key="ing.id" class="border-b border-gray-200 last:border-b-0">
                  <td class="p-2 font-bold">{{ ing.name }}</td>
                  <td class="p-2 text-right font-bold text-indigo-electric">{{ parseFloat(ing.quantity).toFixed(2) }}</td>
                  <td class="p-2 text-right text-gray-graphite/80">{{ ing.unit_of_measure }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>
      </div>

      <div class="flex flex-col gap-8">
        <div class="grid grid-cols-2 gap-4">
          <div class="bg-white p-4 rounded-md border-2 border-gray-graphite text-center">
            <span class="block font-display text-sm font-bold text-gray-graphite/70">STOCK ACTUAL</span>
            <span class="block font-display text-4xl font-extrabold text-indigo-electric">{{ selectedProduct.stock }}</span>
            <span class="block font-bold text-gray-graphite/90">Unidades</span>
          </div>
          <div class="bg-white p-4 rounded-md border-2 border-gray-graphite text-center">
            <span class="block font-display text-sm font-bold text-gray-graphite/70">PRECIO VENTA</span>
            <span class="block font-display text-4xl font-extrabold text-indigo-electric">C${{ parseFloat(selectedProduct.sale_price).toFixed(2) }}</span>
            <span class="block font-bold text-gray-graphite/90">C/U</span>
          </div>
        </div>

        <article class="bg-white p-6 rounded-lg border-2 border-gray-graphite shadow-[8px_8px_0px_#1F2937]">
          <h3 class="font-display text-xl font-bold text-gray-graphite mb-4">Evolución de Stock (por Producción)</h3>
          <!-- INICIO: CORRECCIÓN DEL RENDERIZADO DEL GRÁFICO -->
          <div v-if="stockEvolutionData">
            <canvas v-if="stockEvolutionData.data.length > 0" id="stockChart"></canvas>
            <div v-else class="text-center py-8 text-gray-500">
              <p>No hay datos históricos de producción para mostrar.</p>
            </div>
          </div>
          <div v-else class="text-center py-8 text-gray-500">
             <p>Cargando datos del gráfico...</p>
          </div>
          <!-- FIN: CORRECCIÓN DEL RENDERIZADO DEL GRÁFICO -->
        </article>
      </div>
    </div>

    <Modal :show="isRecipeModalOpen" @close="isRecipeModalOpen = false" title="Gestionar Receta de Producto" size="5xl">
      <RecipeManagementModal v-if="isRecipeModalOpen && selectedProduct" :initial-ingredients="selectedProduct.recipe_ingredients || []" @close="isRecipeModalOpen = false" @save="handleRecipeSave" />
    </Modal>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref, watch, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import { useProductStore } from '../stores/product';
import { storeToRefs } from 'pinia';
import Modal from '../components/Modal.vue';
import RecipeManagementModal from '../components/RecipeManagementModal.vue';

const route = useRoute();
const productStore = useProductStore();
const { selectedProduct, isLoadingDetail, error, stockEvolutionData } = storeToRefs(productStore);
const productId = route.params.id;
let stockChart = null;
const isRecipeModalOpen = ref(false);

const handleRecipeSave = (newRecipe) => {
  if (!selectedProduct.value) return;
  const finalPayload = { recipe_ingredients: newRecipe, };
  productStore.updateProduct(productId, finalPayload, 'detail');
};

const createChart = (labels, data) => {
  if (stockChart) stockChart.destroy();
  const ctx = document.getElementById('stockChart');
  if (!ctx) return;
  stockChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Stock Acumulado',
        data: data,
        fill: false,
        borderColor: '#4F46E5',
        backgroundColor: '#4F46E5',
        tension: 0.1
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true } }
    }
  });
};

watch(stockEvolutionData, (newData) => {
  if (newData && newData.data.length > 0) {
    nextTick(() => {
      createChart(newData.labels, newData.data);
    });
  }
});

onMounted(() => {
  productStore.fetchProductById(productId);
  productStore.fetchStockEvolution(productId);
});

onUnmounted(() => {
  productStore.clearDetailState();
  if (stockChart) {
    stockChart.destroy();
  }
});
</script>