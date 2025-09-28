<template>
  <div>
    <router-link :to="{ name: 'Inventory' }" class="inline-flex items-center gap-2 font-bold text-indigo-electric hover:underline mb-6 group">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5 transition-transform group-hover:-translate-x-1">
        <path fill-rule="evenodd" d="M17 10a.75.75 0 01-.75.75H5.612l4.158 3.96a.75.75 0 11-1.04 1.08l-5.5-5.25a.75.75 0 010-1.08l5.5-5.25a.75.75 0 111.04 1.08L5.612 9.25H16.25A.75.75 0 0117 10z" clip-rule="evenodd" />
      </svg>
      Volver a Inventario
    </router-link>

    <div v-if="isLoadingDetail" class="text-center p-12">
      <p class="font-bold">Cargando detalles de la materia prima...</p>
    </div>
    <div v-else-if="error && !selectedRawMaterial" class="bg-magenta-vibrant/10 text-magenta-vibrant font-bold p-4 rounded-md text-center">
      <p>{{ error }}</p>
    </div>

    <div v-else-if="selectedRawMaterial">

      <article class="bg-white p-6 md:p-8 rounded-lg border-2 border-gray-graphite shadow-[8px_8px_0px_#1F2937] mb-12">
        <div class="flex flex-col md:flex-row md:justify-between md:items-start gap-4">
          <div>
            <h1 class="font-display text-4xl lg:text-5xl font-extrabold text-gray-graphite">{{ selectedRawMaterial.name }}</h1>
            <p class="mt-2 text-lg text-gray-graphite/80">{{ selectedRawMaterial.description || 'Sin descripción detallada.' }}</p>
          </div>
          <div class="bg-white-cloud p-4 rounded-md border-2 border-gray-graphite text-center shrink-0 mt-4 md:mt-0">
            <span class="block font-display text-sm font-bold text-gray-graphite/70">STOCK TOTAL</span>
            <span class="block font-display text-4xl font-extrabold text-indigo-electric">{{ totalStock }}</span>
            <span class="block font-bold text-gray-graphite/90">{{ selectedRawMaterial.unit_of_measure }}</span>
          </div>
        </div>
      </article>

      <div>
        <div class="flex flex-col md:flex-row md:justify-between md:items-center mb-8 gap-4">
          <h2 class="font-display text-3xl font-extrabold text-gray-graphite">Lotes de Compra</h2>
          <button @click="openCreateBatchModal" class="font-bold bg-cyan-energetic text-white py-2 px-6 rounded-md border-2 border-gray-graphite shadow-[4px_4px_0px_#1F2937] hover:shadow-[2px_2px_0px_#1F2937] active:translate-x-[2px] active:translate-y-[2px] active:shadow-none transition-all self-start md:self-center">
            + Añadir Lote
          </button>
        </div>

        <div v-if="!isLoadingBatches && purchaseBatches.length === 0" class="text-center border-2 border-dashed border-gray-400 p-12 rounded-lg">
          <h3 class="font-display font-bold text-xl text-gray-graphite">Sin lotes de compra</h3>
          <p class="text-gray-graphite/80 mt-2">Aún no has registrado ninguna compra para esta materia prima.</p>
        </div>

        <DataTable
          v-else
          :columns="tableColumns"
          :items="purchaseBatches"
          :is-loading="isLoadingBatches"
          :pagination="batchesPagination"
          :current-sort="currentSortState"
          @change-page="handleChangePage"
          @sort-change="handleSortChange"
        >
          <template #cell(quantity)="{ item }">
            {{ item.quantity }} <span class="text-gray-graphite/60">{{ selectedRawMaterial.unit_of_measure }}</span>
          </template>
          <template #cell(total_cost)="{ item }">
            <span class="font-bold text-gray-graphite">C${{ parseFloat(item.total_cost).toFixed(2) }}</span>
          </template>
          <template #cell(actions)="{ item }">
            <div class="flex justify-end items-center space-x-4">
              <button @click="openEditBatchModal(item)" class="font-bold text-indigo-electric hover:underline">Editar</button>
              <button @click="openDeleteBatchModal(item)" class="font-bold text-magenta-vibrant hover:underline">Eliminar</button>
            </div>
          </template>
        </DataTable>
      </div>
    </div>

    <Modal :show="isBatchFormModalOpen" @close="closeBatchFormModal" :title="batchFormModalTitle">
      <PurchaseBatchForm v-if="selectedRawMaterial" :raw-material-id="selectedRawMaterial.id" :initial-data="selectedBatch" @close="closeBatchFormModal" />
    </Modal>

    <ConfirmationModal v-if="batchToDelete" :show="isDeleteBatchModalOpen" title="Confirmar Eliminación de Lote" confirm-text="Sí, Eliminar" @close="closeDeleteBatchModal" @confirm="confirmDeleteBatch">
      <p class="text-gray-graphite">
        ¿Estás seguro de que quieres eliminar este lote comprado el
        <strong class="font-bold text-magenta-vibrant">{{ batchToDelete.purchase_date }}</strong>?
        Esta acción no se puede deshacer.
      </p>
    </ConfirmationModal>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref, computed } from 'vue';
import { useRoute } from 'vue-router';
import { useInventoryStore } from '../stores/inventory';
import { storeToRefs } from 'pinia';
import Modal from '../components/Modal.vue';
import PurchaseBatchForm from '../components/PurchaseBatchForm.vue';
import ConfirmationModal from '../components/ConfirmationModal.vue';
import DataTable from '../components/DataTable.vue';

const route = useRoute();
const inventoryStore = useInventoryStore();
const { selectedRawMaterial, purchaseBatches, isLoadingDetail, isLoadingBatches, error, batchesPagination, batchesOrdering } = storeToRefs(inventoryStore);
const materialId = route.params.id;
const tableColumns = [
  { key: 'purchase_date', label: 'Fecha de Compra', sortable: true },
  { key: 'quantity', label: 'Cantidad' },
  { key: 'total_cost', label: 'Costo Total' },
  { key: 'actions', label: 'Acciones', headerClass: 'text-right', cellClass: 'text-right w-px whitespace-nowrap' },
];

const totalStock = computed(() => {
  if (!Array.isArray(purchaseBatches.value)) return 0;
  const total = purchaseBatches.value.reduce((sum, batch) => sum + parseFloat(batch.quantity), 0);
  return Number.isInteger(total) ? total : total.toFixed(2);
});

const currentSortState = computed(() => {
  if (batchesOrdering.value.startsWith('-')) { return { key: batchesOrdering.value.substring(1), direction: 'desc' }; }
  if (batchesOrdering.value) { return { key: batchesOrdering.value, direction: 'asc' }; }
  return { key: '', direction: '' };
});

const isBatchFormModalOpen = ref(false);
const selectedBatch = ref(null);
const batchFormModalTitle = computed(() => selectedBatch.value ? 'Editar Lote de Compra' : 'Añadir Nuevo Lote de Compra');

const handleChangePage = (newPage) => { inventoryStore.fetchPurchaseBatches(materialId, newPage); };
const handleSortChange = (columnKey) => { inventoryStore.setBatchesOrdering(materialId, columnKey); };
const openCreateBatchModal = () => { selectedBatch.value = null; isBatchFormModalOpen.value = true; };
const openEditBatchModal = (batch) => { selectedBatch.value = { ...batch }; isBatchFormModalOpen.value = true; };
const closeBatchFormModal = () => { isBatchFormModalOpen.value = false; selectedBatch.value = null; };

const isDeleteBatchModalOpen = ref(false);
const batchToDelete = ref(null);

const openDeleteBatchModal = (batch) => { batchToDelete.value = batch; isDeleteBatchModalOpen.value = true; };
const closeDeleteBatchModal = () => { isDeleteBatchModalOpen.value = false; setTimeout(() => { batchToDelete.value = null; }, 300); };
const confirmDeleteBatch = async () => { if (batchToDelete.value) { await inventoryStore.deletePurchaseBatch(batchToDelete.value.id, materialId); closeDeleteBatchModal(); } };

onMounted(() => {
  inventoryStore.fetchRawMaterialById(materialId);
  inventoryStore.fetchPurchaseBatches(materialId, 1);
});

onUnmounted(() => {
  inventoryStore.clearDetailState();
});
</script>