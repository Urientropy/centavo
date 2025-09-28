<template>
  <form @submit.prevent="handleSubmit" class="space-y-6" autocomplete="off">
    <div v-if="formError" class="bg-magenta-vibrant/10 text-magenta-vibrant text-sm font-bold p-3 rounded-md text-center">
      {{ formError }}
    </div>

    <!-- Campo Nombre -->
    <div>
      <label for="name" class="block font-bold text-sm text-gray-graphite mb-2">Nombre del Producto</label>
      <input
        type="text"
        id="name"
        v-model="formData.name"
        required
        class="w-full px-4 py-2 border-2 border-gray-graphite rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-energetic transition"
      >
      <span v-if="errors.name" class="text-magenta-vibrant text-xs mt-1">{{ errors.name[0] }}</span>
    </div>

    <!-- Campo Categoría -->
    <div>
      <label for="category" class="block font-bold text-sm text-gray-graphite mb-2">Categoría (Opcional)</label>
      <input
        type="text"
        id="category"
        v-model="formData.category"
        class="w-full px-4 py-2 border-2 border-gray-graphite rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-energetic transition"
      >
      <span v-if="errors.category" class="text-magenta-vibrant text-xs mt-1">{{ errors.category[0] }}</span>
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

    <!-- Campo Precio de Venta -->
    <div>
      <label for="sale_price" class="block font-bold text-sm text-gray-graphite mb-2">Precio de Venta (Opcional)</label>
      <div class="relative">
        <span class="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-graphite font-bold">$</span>
        <input
          type="number"
          id="sale_price"
          v-model="formData.sale_price"
          step="0.01"
          placeholder="Ej. 150.00"
          class="w-full pl-7 pr-4 py-2 border-2 border-gray-graphite rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-energetic transition"
        >
      </div>
      <span v-if="errors.sale_price" class="text-magenta-vibrant text-xs mt-1">{{ errors.sale_price[0] }}</span>
    </div>

    <!-- Botones de Acción -->
    <div class="flex justify-end gap-4 pt-4">
      <button
        type="button"
        @click="$emit('close')"
        class="bg-white text-gray-graphite font-bold py-2 px-6 rounded-md border-2 border-gray-graphite"
      >
        Cancelar
      </button>
      <button
        type="submit"
        :disabled="isLoading"
        class="bg-indigo-electric text-white font-bold py-2 px-6 rounded-md border-2 border-gray-graphite shadow-[4px_4px_0px_#1F2937] hover:shadow-[2px_2px_0px_#1F2937] active:translate-x-[2px] active:translate-y-[2px] active:shadow-none transition-all disabled:bg-gray-400"
      >
        <span v-if="isLoading">Guardando...</span>
        <span v-else>{{ isEditing ? 'Actualizar Producto' : 'Guardar Producto' }}</span>
      </button>
    </div>
  </form>
</template>

<script setup>
import { reactive, ref, computed, watch } from 'vue';
import { useProductStore } from '../stores/product';

const props = defineProps({
  initialData: { type: Object, default: null },
});
const emit = defineEmits(['close']);

const productStore = useProductStore();

const formData = reactive({
  id: props.initialData?.id || null,
  name: props.initialData?.name || '',
  category: props.initialData?.category || '',
  description: props.initialData?.description || '',
  sale_price: props.initialData?.sale_price || '',
});

const errors = ref({});
const formError = ref(null); // Para errores globales como "Nombre duplicado"
const isLoading = ref(false);

const isEditing = computed(() => !!props.initialData);

watch(() => props.initialData, (newData) => {
  formData.id = newData?.id || null;
  formData.name = newData?.name || '';
  formData.category = newData?.category || '';
  formData.description = newData?.description || '';
  formData.sale_price = newData?.sale_price || '';
  errors.value = {};
  formError.value = null;
});

const handleSubmit = async () => {
  isLoading.value = true;
  errors.value = {};
  formError.value = null;

  // El backend espera `null` para el precio si está vacío, no un string vacío.
  const payload = { ...formData };
  if (!payload.sale_price) {
    payload.sale_price = null;
  }

  const actionPromise = isEditing.value
    ? productStore.updateProduct(payload.id, payload)
    : productStore.createProduct(payload);

  emit('close');

  try {
    await actionPromise;
  } catch (error) {
    if (error.response && error.response.status === 400) {
      // Si el error tiene 'detail', es un error global.
      if (error.response.data.detail) {
        formError.value = error.response.data.detail;
      } else {
        // Si no, son errores de campo.
        errors.value = error.response.data;
      }
      // Reabrir el modal si hay error. La vista padre necesita manejar esto.
      // Por ahora, se loguea en consola.
      console.error("Error de validación:", error.response.data);
    } else {
      console.error("Error inesperado al guardar producto:", error);
      formError.value = "Ocurrió un error inesperado."
    }
  } finally {
    isLoading.value = false;
  }
};
</script>
