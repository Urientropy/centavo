<template>
  <Modal :show="show" @close="$emit('close')" :title="title">
    <div>
      <!-- Usamos un <slot> para permitir mensajes más complejos si es necesario,
           con un mensaje por defecto que se muestra si no se provee contenido. -->
      <slot>
        <p class="text-gray-graphite">{{ message }}</p>
      </slot>

      <div class="flex justify-end gap-4 mt-8">
        <button
          @click="$emit('close')"
          class="bg-white text-gray-graphite font-bold py-2 px-6 rounded-md border-2 border-gray-graphite"
        >
          {{ cancelText }}
        </button>
        <button
          @click="$emit('confirm')"
          class="bg-magenta-vibrant text-white font-bold py-2 px-6 rounded-md border-2 border-gray-graphite shadow-[4px_4px_0px_#1F2937] hover:shadow-[2px_2px_0px_#1F2937] active:translate-x-[2px] active:translate-y-[2px] active:shadow-none transition-all"
        >
          {{ confirmText }}
        </button>
      </div>
    </div>
  </Modal>
</template>

<script setup>
import Modal from './Modal.vue';

defineProps({
  show: { type: Boolean, required: true },
  title: { type: String, default: 'Confirmar Acción' },
  message: { type: String, default: '¿Estás seguro de que quieres realizar esta acción?' },
  confirmText: { type: String, default: 'Confirmar' },
  cancelText: { type: String, default: 'Cancelar' },
});

defineEmits(['close', 'confirm']);
</script>