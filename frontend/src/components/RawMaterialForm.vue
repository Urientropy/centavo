<template>
  <form @submit.prevent="handleSubmit" class="space-y-6" autocomplete="off">
    <!-- Campo Nombre -->
    <div>
      <label for="name" class="block font-bold text-sm text-gray-graphite mb-2">Nombre</label>
      <input
        type="text"
        id="name"
        v-model="formData.name"
        required
        autocomplete="off"
        class="w-full px-4 py-2 border-2 border-gray-graphite rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-energetic transition"
      >
      <span v-if="errors.name" class="text-magenta-vibrant text-xs mt-1">{{ errors.name[0] }}</span>
    </div>

    <!-- Campo Unidad de Medida -->
    <div>
      <label for="unit_of_measure" class="block font-bold text-sm text-gray-graphite mb-2">Unidad de Medida</label>
      <input
        type="text"
        id="unit_of_measure"
        v-model="formData.unit_of_measure"
        required
        autocomplete="off"
        placeholder="Ej. Kilogramo (kg), Litro (L), Unidad"
        class="w-full px-4 py-2 border-2 border-gray-graphite rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-energetic transition"
      >
      <span v-if="errors.unit_of_measure" class="text-magenta-vibrant text-xs mt-1">{{ errors.unit_of_measure[0] }}</span>
    </div>

    <!-- Campo Descripción -->
    <div>
      <label for="description" class="block font-bold text-sm text-gray-graphite mb-2">Descripción (Opcional)</label>
      <textarea
        id="description"
        v-model="formData.description"
        rows="3"
        class="w-full px-4 py-2 border-2 border-gray-graphite rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-energetic transition"
      ></textarea>
      <span v-if="errors.description" class="text-magenta-vibrant text-xs mt-1">{{ errors.description[0] }}</span>
    </div>

    <!-- Botones de Acción -->
    <div class="flex justify-end gap-4 pt-4">
      <button
        type="button"
        @click="$emit('close')"
        class="bg-white text-gray-graphite font-bold py-2 px-6 rounded-md border-2 border-gray-graphite" >
        Cancelar
      </button>
      <button
        type="submit"
        :disabled="isLoading"
        class="bg-indigo-electric text-white font-bold py-2 px-6 rounded-md border-2 border-gray-graphite shadow-[4px_4px_0px_#1F2937] hover:shadow-[2px_2px_0px_#1F2937] active:translate-x-[2px] active:translate-y-[2px] active:shadow-none transition-all disabled:bg-gray-400">
        <span v-if="isLoading">Guardando...</span>
        <span v-else>{{ isEditing ? 'Actualizar' : 'Guardar' }}</span>
      </button>
    </div>
  </form>
</template>

<script setup>
import { reactive, ref, watch, computed } from 'vue';
import { useInventoryStore } from '../stores/inventory';

// 1. Definimos las props y emits
const props = defineProps({
  initialData: {
    type: Object,
    default: null,
  },
});
const emit = defineEmits(['close', 'success']);

const inventoryStore = useInventoryStore();

// 2. Estado del formulario (se inicializa vacío o con initialData)
const formData = reactive({
  id: props.initialData?.id || null,
  name: props.initialData?.name || '',
  unit_of_measure: props.initialData?.unit_of_measure || '',
  description: props.initialData?.description || '',
});

const errors = ref({});
const isLoading = ref(false);

// 3. Computed para saber si estamos en modo edición
const isEditing = computed(() => !!props.initialData);

// 4. Observador para resetear el formulario si initialData cambia
watch(() => props.initialData, (newData) => {
  formData.id = newData?.id || null;
  formData.name = newData?.name || '';
  formData.unit_of_measure = newData?.unit_of_measure || '';
  formData.description = newData?.description || '';
  errors.value = {}; // Limpiar errores
});

// 5. El manejador ahora decide si crear o actualizar
const handleSubmit = async () => {
  isLoading.value = true;
  errors.value = {};
  try {
    if (isEditing.value) {
      await inventoryStore.updateRawMaterial(formData.id, formData);
    } else {
      await inventoryStore.createRawMaterial(formData);
    }
    emit('success');
    emit('close');
  } catch (error) {
    if (error.response && error.response.status === 400) {
      errors.value = error.response.data;
    } else {
      console.error("Error inesperado:", error);
    }
  } finally {
    isLoading.value = false;
  }
};
</script>