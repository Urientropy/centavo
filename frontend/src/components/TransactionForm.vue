<template>
  <form @submit.prevent="handleSubmit">
    <div class="space-y-4">
      <div>
        <label for="description" class="block font-bold text-gray-graphite mb-1">Descripción</label>
        <input
          id="description"
          type="text"
          v-model="form.description"
          required
          :placeholder="`Ej: ${transactionType === 'income' ? 'Venta de tortas' : 'Compra de harina'}`"
          class="w-full px-4 py-2 border-2 border-gray-graphite rounded-md focus:ring-2 focus:ring-cyan-energetic focus:outline-none transition"
        />
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div>
          <label for="amount" class="block font-bold text-gray-graphite mb-1">Monto</label>
          <input
            id="amount"
            type="number"
            v-model="form.amount"
            required
            min="0.01"
            step="0.01"
            placeholder="Ej: 150.75"
            class="w-full px-4 py-2 border-2 border-gray-graphite rounded-md focus:ring-2 focus:ring-cyan-energetic focus:outline-none transition"
          />
        </div>
        <div>
          <label for="date" class="block font-bold text-gray-graphite mb-1">Fecha</label>
          <input
            id="date"
            type="date"
            v-model="form.date"
            required
            class="w-full px-4 py-2 border-2 border-gray-graphite rounded-md focus:ring-2 focus:ring-cyan-energetic focus:outline-none transition bg-white"
          />
        </div>
      </div>
    </div>

    <!-- Mensaje de Error (si se pasa como prop) -->
    <div v-if="error" class="mt-4 p-3 rounded-md bg-magenta-vibrant/10 text-magenta-vibrant text-sm">
      <p><strong class="font-bold">Error:</strong> {{ error }}</p>
    </div>

    <div class="flex justify-end items-center pt-6 border-t-2 border-gray-graphite/10 mt-6">
      <button @click="$emit('close')" type="button" class="font-bold text-gray-graphite py-2 px-6 rounded-md hover:bg-gray-graphite/10 transition-colors">
        Cancelar
      </button>
      <button
        type="submit"
        :disabled="isSubmitting"
        class="font-bold bg-cyan-energetic text-white py-2 px-6 rounded-md border-2 border-gray-graphite shadow-[4px_4px_0px_#1F2937] hover:shadow-[2px_2px_0px_#1F2937] active:translate-x-[2px] active:translate-y-[2px] active:shadow-none transition-all ml-4 disabled:bg-gray-400 disabled:shadow-none disabled:cursor-not-allowed"
      >
        <span v-if="isSubmitting">Guardando...</span>
        <span v-else>Guardar</span>
      </button>
    </div>
  </form>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  initialData: {
    type: Object,
    default: () => ({ description: '', amount: '', date: new Date().toISOString().slice(0, 10) })
  },
  isSubmitting: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  },
  transactionType: {
    type: String,
    default: 'income' // 'income' or 'expense'
  }
});

const emit = defineEmits(['submit', 'close']);

const form = ref({ ...props.initialData });

// Sincroniza el formulario si los datos iniciales cambian (útil para el modo de edición)
watch(() => props.initialData, (newData) => {
  form.value = { ...newData };
});

const handleSubmit = () => {
  // El formulario solo emite los datos, no sabe si está creando o editando.
  // La vista padre se encargará de esa lógica.
  emit('submit', form.value);
};
</script>