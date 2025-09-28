<template>
  <div class="bg-white rounded-lg border-2 border-gray-graphite shadow-[8px_8px_0px_#1F2937] overflow-hidden">
    <div class="overflow-x-auto">
      <table class="w-full">
        <thead class="border-b-2 border-gray-graphite bg-white">
          <tr>
            <th
              v-for="column in columns"
              :key="column.key"
              class="text-left p-4 font-display font-bold"
              :class="[column.headerClass, { 'cursor-pointer hover:bg-gray-graphite/5': column.sortable }]"
              @click="column.sortable ? $emit('sort-change', column.key) : null"
            >
              <div class="flex items-center gap-2">
                <span>{{ column.label }}</span>
                <div v-if="column.sortable" class="w-4 h-4 text-gray-graphite">
                  <svg v-if="currentSort.key === column.key && currentSort.direction === 'asc'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5">
                    <path fill-rule="evenodd" d="M10 17a.75.75 0 01-.75-.75V5.612L5.29 9.57a.75.75 0 01-1.08-1.04l5.25-5.5a.75.75 0 011.08 0l5.25 5.5a.75.75 0 11-1.08 1.04L10.75 5.612V16.25A.75.75 0 0110 17z" clip-rule="evenodd" />
                  </svg>
                  <svg v-else-if="currentSort.key === column.key && currentSort.direction === 'desc'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5">
                    <path fill-rule="evenodd" d="M10 3a.75.75 0 01.75.75v10.638l3.96-3.96a.75.75 0 111.08 1.04l-5.25 5.25a.75.75 0 01-1.08 0l-5.25-5.25a.75.75 0 111.08-1.04l3.96 3.96V3.75A.75.75 0 0110 3z" clip-rule="evenodd" />
                  </svg>
                </div>
              </div>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="isLoading">
            <td :colspan="columns.length" class="text-center p-12">
              <p class="font-bold">Cargando datos...</p>
            </td>
          </tr>
          <!-- La condición v-else-if="items.length === 0" ahora funciona de forma segura -->
          <tr v-else-if="items.length === 0">
            <td :colspan="columns.length" class="text-center p-12">
              <p class="font-bold text-gray-graphite">No se encontraron resultados.</p>
            </td>
          </tr>
          <tr
            v-for="(item, index) in items"
            :key="item.id || index"
            v-else
            class="border-b border-gray-200 last:border-b-0 hover:bg-white-cloud transition-colors"
          >
            <td
              v-for="column in columns"
              :key="column.key"
              class="p-4"
              :class="column.cellClass"
            >
              <slot :name="`cell(${column.key})`" :item="item">
                {{ item[column.key] || 'N/A' }}
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="!isLoading && pagination.totalPages > 1" class="flex justify-between items-center p-4 border-t-2 border-gray-graphite bg-white">
        <button
          @click="$emit('change-page', pagination.page - 1)"
          :disabled="pagination.page <= 1"
          class="pagination-button"
        >
          Anterior
        </button>
        <span class="font-bold text-sm text-gray-graphite">
          Página {{ pagination.page }} de {{ pagination.totalPages }}
        </span>
        <button
          @click="$emit('change-page', pagination.page + 1)"
          :disabled="pagination.page >= pagination.totalPages"
          class="pagination-button"
        >
          Siguiente
        </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  columns: { type: Array, required: true },
  // --- LA CORRECCIÓN ESTÁ AQUÍ ---
  items: {
    type: Array,
    // required: false, // Ya no es requerida
    default: () => [], // Tiene un valor por defecto seguro
  },
  isLoading: { type: Boolean, default: false },
  pagination: {
    type: Object,
    default: () => ({ page: 1, totalPages: 1 }),
  },
  currentSort: {
    type: Object,
    default: () => ({ key: '', direction: '' }),
  },
});

defineEmits(['change-page', 'sort-change']);
</script>

<style scoped>
.pagination-button {
  @apply font-bold bg-indigo-electric text-white py-2 px-4 rounded-md border-2 border-gray-graphite
         shadow-[2px_2px_0px_#1F2937] hover:shadow-[1px_1px_0px_#1F2937]
         active:translate-x-[1px] active:translate-y-[1px] active:shadow-none
         transition-all disabled:bg-gray-400 disabled:shadow-none disabled:cursor-not-allowed;
}
</style>