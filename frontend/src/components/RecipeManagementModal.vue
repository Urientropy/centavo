<template>
  <div class="flex flex-col h-[70vh]">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 flex-1 overflow-hidden">

      <div class="flex flex-col h-full overflow-hidden">
        <h3 class="font-display font-bold text-lg text-gray-graphite mb-2">Añadir Ingredientes</h3>
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Buscar materia prima..."
          class="w-full px-4 py-2 border-2 border-gray-graphite rounded-md focus:ring-2 focus:ring-cyan-energetic focus:outline-none transition mb-4"
        />
        <div class="flex-1 overflow-y-auto border-2 border-gray-graphite/20 rounded-md p-2 bg-white-cloud">
          <div v-if="isSearching" class="text-center p-4">Cargando...</div>
          <div v-else-if="searchResults.length === 0 && searchQuery" class="text-center p-4 text-gray-500">No se encontraron resultados.</div>
          <ul v-else>
            <li v-for="material in searchResults" :key="material.id">
              <button
                @click="addIngredient(material)"
                :disabled="isIngredientAdded(material.id)"
                class="w-full text-left p-3 rounded-md flex justify-between items-center transition-colors"
                :class="{
                  'hover:bg-indigo-electric/10': !isIngredientAdded(material.id),
                  'opacity-50 cursor-not-allowed': isIngredientAdded(material.id)
                }"
              >
                <div>
                  <span class="font-bold">{{ material.name }}</span>
                  <span class="text-sm text-gray-500 ml-2">({{ material.unit_of_measure }})</span>
                </div>
                <span v-if="isIngredientAdded(material.id)" class="font-bold text-xs text-cyan-energetic">AÑADIDO</span>
              </button>
            </li>
          </ul>
        </div>
      </div>

      <div class="flex flex-col h-full overflow-hidden">
        <h3 class="font-display font-bold text-lg text-gray-graphite mb-2">Receta Actual ({{ editableIngredients.length }} ingredientes)</h3>
        <div class="flex-1 overflow-y-auto border-2 border-gray-graphite/20 rounded-md p-2 bg-white-cloud">
          <div v-if="editableIngredients.length === 0" class="text-center p-10 text-gray-500">
            <p>Añade ingredientes desde la búsqueda.</p>
          </div>
          <ul v-else class="space-y-2">
            <li v-for="(ingredient, index) in editableIngredients" :key="ingredient.raw_material_id" class="bg-white p-3 rounded-md border-2 border-gray-graphite/10 flex items-center gap-4">
              <div class="flex-1">
                <p class="font-bold">{{ ingredient.name }}</p>
                <div class="flex items-center gap-2 mt-1">
                  <input
                    type="number"
                    v-model="ingredient.quantity"
                    min="0.01"
                    step="0.01"
                    class="w-24 px-2 py-1 border-2 border-gray-graphite/50 rounded-md focus:ring-2 focus:ring-cyan-energetic focus:outline-none"
                  />
                  <span class="text-sm text-gray-600">{{ ingredient.unit_of_measure }}</span>
                </div>
              </div>
              <button @click="removeIngredient(index)" class="p-2 text-magenta-vibrant hover:bg-magenta-vibrant/10 rounded-full">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5"><path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" /></svg>
              </button>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <div class="flex justify-end items-center pt-6 border-t-2 border-gray-graphite/10 mt-6">
      <button @click="$emit('close')" class="font-bold text-gray-graphite py-2 px-6 rounded-md hover:bg-gray-graphite/10 transition-colors">Cancelar</button>
      <button
        @click="handleSave"
        class="font-bold bg-indigo-electric text-white py-2 px-6 rounded-md border-2 border-gray-graphite shadow-[4px_4px_0px_#1F2937] hover:shadow-[2px_2px_0px_#1F2937] active:translate-x-[2px] active:translate-y-[2px] active:shadow-none transition-all ml-4"
      >
        Guardar Cambios
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import apiClient from '../services/api';

const props = defineProps({
  initialIngredients: {
    type: Array,
    default: () => [],
  },
});
const emit = defineEmits(['close', 'save']);

const editableIngredients = ref([]);
const searchQuery = ref('');
const searchResults = ref([]);
const isSearching = ref(false);
let debounceTimer = null;

onMounted(() => {
  editableIngredients.value = props.initialIngredients.map(ing => {
    return {
      raw_material_id: ing.id,
      name: ing.name,
      unit_of_measure: ing.unit_of_measure,
      quantity: ing.quantity
    };
  });
});

const isIngredientAdded = (materialId) => {
  return editableIngredients.value.some(ing => ing.raw_material_id === materialId);
};

const addIngredient = (material) => {
  if (isIngredientAdded(material.id)) return;
  editableIngredients.value.push({
    raw_material_id: material.id,
    name: material.name,
    unit_of_measure: material.unit_of_measure,
    quantity: '1.00'
  });
};

const removeIngredient = (index) => {
  editableIngredients.value.splice(index, 1);
};

// --- INICIO: CORRECCIÓN DEL PAYLOAD DE GUARDADO ---
const handleSave = () => {
  const payload = editableIngredients.value.map(ing => ({
    // El serializer espera 'raw_material', no 'raw_material_id'.
    // El valor debe ser el ID.
    raw_material: ing.raw_material_id,
    quantity: ing.quantity,
  }));
  emit('save', payload);
  emit('close');
};
// --- FIN: CORRECCIÓN DEL PAYLOAD DE GUARDADO ---

watch(searchQuery, (newQuery) => {
  clearTimeout(debounceTimer);
  isSearching.value = true;
  debounceTimer = setTimeout(async () => {
    if (newQuery.trim()) {
      try {
        const response = await apiClient.get(`/inventory/raw-materials/?search=${newQuery.trim()}`);
        searchResults.value = response.data.results || response.data;
      } catch (error) {
        console.error("Error buscando materias primas:", error);
        searchResults.value = [];
      } finally {
        isSearching.value = false;
      }
    } else {
      searchResults.value = [];
      isSearching.value = false;
    }
  }, 300);
});
</script>