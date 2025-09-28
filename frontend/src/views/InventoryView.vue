<template>
  <div>
    <!-- BLOQUE DE CARGA INICIAL -->
    <div v-if="isLoadingInitialData" class="text-center p-12">
      <p class="font-display font-bold text-xl text-gray-graphite">Cargando inventario...</p>
    </div>

    <!-- CONTENIDO PRINCIPAL -->
    <div v-else>
      <div class="flex flex-col md:flex-row md:justify-between md:items-center mb-8 gap-4">
        <h1 class="font-display text-4xl font-extrabold text-gray-graphite">Materias Primas</h1>
        <button @click="openCreateModal" class="font-bold bg-cyan-energetic text-white py-2 px-6 rounded-md border-2 border-gray-graphite shadow-[4px_4px_0px_#1F2937] hover:shadow-[2px_2px_0px_#1F2937] active:translate-x-[2px] active:translate-y-[2px] active:shadow-none transition-all self-start md:self-center">
          + Añadir Materia Prima
        </button>
      </div>

      <div class="flex flex-col md:flex-row gap-4 mb-6">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Buscar por nombre o descripción..."
          class="w-full md:max-w-sm px-4 py-2 border-2 border-gray-graphite rounded-md focus:ring-2 focus:ring-cyan-energetic focus:outline-none transition"
        />
        <select
          v-model="selectedUnit"
          @change="handleUnitFilterChange"
          class="w-full md:w-auto px-4 py-2 border-2 border-gray-graphite rounded-md focus:ring-2 focus:ring-cyan-energetic focus:outline-none transition bg-white"
        >
          <option v-for="unit in unitsOfMeasure" :key="unit" :value="unit">
            {{ unit === 'Todos' ? 'Todas las unidades' : unit }}
          </option>
        </select>
      </div>

      <div>
        <div v-if="error" class="bg-magenta-vibrant/10 text-magenta-vibrant font-bold p-4 rounded-md text-center mb-8">
          {{ error }}
        </div>

        <div v-if="!isLoadingList && rawMaterials.length === 0 && !error" class="text-center border-2 border-dashed border-gray-400 p-12 rounded-lg">
            <h3 class="font-display font-bold text-xl text-gray-graphite">{{ searchQuery || selectedUnit !== 'Todos' ? 'No hay resultados para tu búsqueda' : 'Aún no tienes materias primas' }}</h3>
            <p class="text-gray-graphite/80 mt-2">{{ searchQuery || selectedUnit !== 'Todos' ? 'Intenta con otros filtros.' : '¡Añade la primera para empezar a organizar tu inventario!' }}</p>
        </div>

        <DataTable
          v-else
          :columns="tableColumns"
          :items="rawMaterials"
          :is-loading="isLoadingList"
          :pagination="pagination"
          :current-sort="currentSortState"
          @change-page="handleChangePage"
          @sort-change="handleSortChange"
        >
          <template #cell(name)="{ item }">
            <router-link
              :to="{ name: 'RawMaterialDetail', params: { id: item.id } }"
              class="font-bold text-indigo-electric hover:underline"
            >
              {{ item.name }}
            </router-link>
          </template>
          <!-- SLOT PARA LA CELDA DE STOCK TOTAL CORREGIDO -->
          <template #cell(total_stock)="{ item }">
            <span class="font-bold text-gray-graphite">{{ item.total_stock }}</span>
          </template>
          <!-- SLOT PARA LA UNIDAD DE MEDIDA (YA NO ESTÁ DENTRO DEL STOCK) -->
          <template #cell(unit_of_measure)="{ item }">
            <span class="text-gray-graphite/80">({{ item.unit_of_measure }})</span>
          </template>
          <template #cell(description)="{ item }">
            <span class="text-gray-graphite/80">{{ item.description || 'N/A' }}</span>
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
        <RawMaterialForm
          :initial-data="selectedMaterial"
          @close="closeFormModal"
        />
      </Modal>

      <ConfirmationModal
        v-if="materialToDelete"
        :show="isDeleteModalOpen"
        title="Confirmar Eliminación"
        confirm-text="Sí, Eliminar"
        @close="closeDeleteModal"
        @confirm="confirmDelete"
      >
        <p class="text-gray-graphite">
          ¿Estás seguro de que quieres eliminar la materia prima
          <strong class="font-bold text-magenta-vibrant">"{{ materialToDelete.name }}"</strong>?
          Esta acción no se puede deshacer.
        </p>
      </ConfirmationModal>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch, computed } from 'vue';
import { useInventoryStore } from '../stores/inventory';
import { storeToRefs } from 'pinia';
import Modal from '../components/Modal.vue';
import RawMaterialForm from '../components/RawMaterialForm.vue';
import ConfirmationModal from '../components/ConfirmationModal.vue';
import DataTable from '../components/DataTable.vue';

const inventoryStore = useInventoryStore();
const { rawMaterials, isLoadingList, error, pagination, unitsOfMeasure, ordering } = storeToRefs(inventoryStore);

const isLoadingInitialData = ref(true);

// --- DEFINICIÓN DE COLUMNAS ACTUALIZADA ---
const tableColumns = [
  { key: 'name', label: 'Nombre', sortable: true },
  {
    key: 'total_stock',
    label: 'Stock Total',
    sortable: true,
    // Eliminamos la alineación a la derecha para que la unidad de medida se vea bien al lado
  },
  { key: 'unit_of_measure', label: 'Unidad de Medida' },
  { key: 'description', label: 'Descripción' },
  {
    key: 'actions',
    label: 'Acciones',
    headerClass: 'text-right',
    cellClass: 'text-right w-px whitespace-nowrap'
  },
];

const isFormModalOpen = ref(false);
const selectedMaterial = ref(null);
const modalTitle = computed(() => selectedMaterial.value ? 'Editar Materia Prima' : 'Añadir Nueva Materia Prima');

const isDeleteModalOpen = ref(false);
const materialToDelete = ref(null);

const searchQuery = ref('');
const selectedUnit = ref('Todos');
let debounceTimer = null;

const currentSortState = computed(() => {
  if (ordering.value.startsWith('-')) {
    return { key: ordering.value.substring(1), direction: 'desc' };
  }
  if (ordering.value) {
    return { key: ordering.value, direction: 'asc' };
  }
  return { key: '', direction: '' };
});

watch(searchQuery, (newQuery) => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    inventoryStore.fetchRawMaterials(1, newQuery);
  }, 300);
});

const handleChangePage = (newPage) => {
  inventoryStore.fetchRawMaterials(newPage, searchQuery.value);
};

const handleSortChange = (columnKey) => {
  searchQuery.value = '';
  inventoryStore.setOrdering(columnKey);
};

const handleUnitFilterChange = () => {
  searchQuery.value = '';
  inventoryStore.setUnitOfMeasureFilter(selectedUnit.value);
};

const openCreateModal = () => {
  selectedMaterial.value = null;
  isFormModalOpen.value = true;
};

const openEditModal = (material) => {
  selectedMaterial.value = { ...material };
  isFormModalOpen.value = true;
};

const closeFormModal = () => {
  isFormModalOpen.value = false;
  selectedMaterial.value = null;
};

const openDeleteModal = (material) => {
  materialToDelete.value = material;
  isDeleteModalOpen.value = true;
};

const closeDeleteModal = () => {
  isDeleteModalOpen.value = false;
  setTimeout(() => {
    materialToDelete.value = null;
  }, 300);
};

const confirmDelete = async () => {
  if (materialToDelete.value) {
    await inventoryStore.deleteRawMaterial(materialToDelete.value.id, searchQuery.value);
    closeDeleteModal();
  }
};

onMounted(async () => {
  try {
    await Promise.all([
      inventoryStore.fetchRawMaterials(1, searchQuery.value),
      inventoryStore.fetchUnitsOfMeasure()
    ]);
  } catch (e) {
    console.error("Fallo durante el montaje inicial:", e);
  } finally {
    isLoadingInitialData.value = false;
  }
});
</script>