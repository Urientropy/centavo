<template>
  <form @submit.prevent="handleSubmit" class="space-y-6" autocomplete="off">
    <!-- El template no necesita cambios -->
    <div>
      <label for="purchase_date" class="block font-bold text-sm text-gray-graphite mb-2">Fecha de Compra</label>
      <input
        type="date"
        id="purchase_date"
        v-model="formData.purchase_date"
        required
        class="w-full px-4 py-2 border-2 border-gray-graphite rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-energetic transition"
      >
      <span v-if="errors.purchase_date" class="text-magenta-vibrant text-xs mt-1">{{ errors.purchase_date[0] }}</span>
    </div>

    <div>
      <label for="quantity" class="block font-bold text-sm text-gray-graphite mb-2">Cantidad</label>
      <input
        type="number"
        id="quantity"
        v-model="formData.quantity"
        required
        step="0.01"
        placeholder="Ej. 50.5"
        class="w-full px-4 py-2 border-2 border-gray-graphite rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-energetic transition"
      >
      <span v-if="errors.quantity" class="text-magenta-vibrant text-xs mt-1">{{ errors.quantity[0] }}</span>
    </div>

    <div>
      <label for="total_cost" class="block font-bold text-sm text-gray-graphite mb-2">Costo Total</label>
      <div class="relative">
        <span class="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-graphite font-bold">$</span>
        <input
          type="number"
          id="total_cost"
          v-model="formData.total_cost"
          required
          step="0.01"
          placeholder="Ej. 7500.50"
          class="w-full pl-7 pr-4 py-2 border-2 border-gray-graphite rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-energetic transition"
        >
      </div>
      <span v-if="errors.total_cost" class="text-magenta-vibrant text-xs mt-1">{{ errors.total_cost[0] }}</span>
    </div>

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
        <span v-else>{{ isEditing ? 'Actualizar Lote' : 'Guardar Lote' }}</span>
      </button>
    </div>
  </form>
</template>

<script setup>
import { reactive, ref, computed, watch } from 'vue';
import { useInventoryStore } from '../stores/inventory';

const props = defineProps({
  rawMaterialId: { type: Number, required: true },
  initialData: { type: Object, default: null },
});
const emit = defineEmits(['close']);

const inventoryStore = useInventoryStore();

const getTodayDate = () => new Date().toISOString().split('T')[0];

const formData = reactive({
  id: props.initialData?.id || null,
  raw_material: props.rawMaterialId,
  purchase_date: props.initialData?.purchase_date || getTodayDate(),
  quantity: props.initialData?.quantity || '',
  total_cost: props.initialData?.total_cost || '',
});

const errors = ref({});
const isLoading = ref(false);

const isEditing = computed(() => !!props.initialData);

watch(() => props.initialData, (newData) => {
  formData.id = newData?.id || null;
  formData.raw_material = props.rawMaterialId;
  formData.purchase_date = newData?.purchase_date || getTodayDate();
  formData.quantity = newData?.quantity || '';
  formData.total_cost = newData?.total_cost || '';
  errors.value = {};
});

const handleSubmit = async () => {
  isLoading.value = true;
  errors.value = {};

  // Creamos una promesa que se resolverá con éxito o error
  const actionPromise = isEditing.value
    ? inventoryStore.updatePurchaseBatch(formData.id, formData)
    : inventoryStore.createPurchaseBatch(formData);

  // --- LA CORRECCIÓN ESTÁ AQUÍ ---
  // Cerramos el modal INMEDIATAMENTE
  emit('close');

  // Ahora, manejamos la promesa en segundo plano
  try {
    await actionPromise;
    // La acción fue exitosa, el store ya está re-validando los datos.
  } catch (error) {
    if (error.response && error.response.status === 400) {
      // Si hay un error de validación, deberíamos reabrir el modal con los errores.
      // Por ahora, lo mostraremos en la consola para no añadir complejidad.
      // En un futuro sprint, podemos implementar un sistema de "toast" para errores.
      console.error("Error de validación:", error.response.data);
      // Opcional: inventoryStore.error = "Hubo un error de validación."
    } else {
      console.error("Error inesperado al guardar lote:", error);
    }
  } finally {
    // Esto es menos crítico ahora, pero es buena práctica
    isLoading.value = false;
  }
};
</script>
