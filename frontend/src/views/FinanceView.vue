<template>
  <div>
    <h1 class="font-display text-4xl font-extrabold text-gray-graphite mb-8">Finanzas</h1>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-x-8 gap-y-12">
      <!-- Columna de Ingresos -->
      <div>
        <h2 class="font-display text-3xl font-bold text-gray-graphite mb-6">Ingresos</h2>
        <div class="flex flex-col md:flex-row gap-4 mb-6">
          <input
            type="text"
            v-model="incomeSearchQuery"
            placeholder="Buscar en ingresos..."
            class="w-full md:flex-1 px-4 py-2 border-2 border-gray-graphite rounded-md focus:ring-2 focus:ring-cyan-energetic focus:outline-none transition"
          />
          <button @click="openModal('income', 'create')" class="font-bold bg-cyan-energetic text-white py-2 px-6 rounded-md border-2 border-gray-graphite shadow-[4px_4px_0px_#1F2937] hover:shadow-[2px_2px_0px_#1F2937] active:translate-x-[2px] active:translate-y-[2px] active:shadow-none transition-all">
            + Añadir Ingreso
          </button>
        </div>
        <DataTable
          :columns="incomeColumns"
          :items="incomes"
          :is-loading="isLoadingIncomes"
          :pagination="incomesPagination"
          :current-sort="currentIncomeSortState"
          @change-page="handleIncomePageChange"
          @sort-change="key => financeStore.setIncomesOrdering(key)"
        >
          <template #cell(date)="{ item }"><span>{{ format(new Date(item.date), 'dd MMM yyyy') }}</span></template>
          <template #cell(amount)="{ item }"><span class="font-bold text-green-600">+ C${{ parseFloat(item.amount).toFixed(2) }}</span></template>
          <template #cell(actions)="{ item }">
            <div class="flex justify-end items-center space-x-4">
              <button @click="openModal('income', 'edit', item)" class="font-bold text-indigo-electric hover:underline">Editar</button>
              <button @click="openDeleteModal('income', item)" class="font-bold text-magenta-vibrant hover:underline">Eliminar</button>
            </div>
          </template>
        </DataTable>
      </div>

      <!-- Columna de Gastos -->
      <div>
        <h2 class="font-display text-3xl font-bold text-gray-graphite mb-6">Gastos</h2>
        <div class="flex flex-col md:flex-row gap-4 mb-6">
           <input
            type="text"
            v-model="expenseSearchQuery"
            placeholder="Buscar en gastos..."
            class="w-full md:flex-1 px-4 py-2 border-2 border-gray-graphite rounded-md focus:ring-2 focus:ring-cyan-energetic focus:outline-none transition"
          />
          <button @click="openModal('expense', 'create')" class="font-bold bg-magenta-vibrant text-white py-2 px-6 rounded-md border-2 border-gray-graphite shadow-[4px_4px_0px_#1F2937] hover:shadow-[2px_2px_0px_#1F2937] active:translate-x-[2px] active:translate-y-[2px] active:shadow-none transition-all">
            + Añadir Gasto
          </button>
        </div>
        <DataTable
          :columns="expenseColumns"
          :items="expenses"
          :is-loading="isLoadingExpenses"
          :pagination="expensesPagination"
          :current-sort="currentExpenseSortState"
          @change-page="handleExpensePageChange"
          @sort-change="key => financeStore.setExpensesOrdering(key)"
        >
          <template #cell(date)="{ item }"><span>{{ format(new Date(item.date), 'dd MMM yyyy') }}</span></template>
           <template #cell(amount)="{ item }"><span class="font-bold text-red-600">- C${{ parseFloat(item.amount).toFixed(2) }}</span></template>
          <template #cell(actions)="{ item }">
            <div class="flex justify-end items-center space-x-4">
              <button @click="openModal('expense', 'edit', item)" class="font-bold text-indigo-electric hover:underline">Editar</button>
              <button @click="openDeleteModal('expense', item)" class="font-bold text-magenta-vibrant hover:underline">Eliminar</button>
            </div>
          </template>
        </DataTable>
      </div>
    </div>

    <Modal :show="isFormModalOpen" @close="closeFormModal" :title="modalTitle">
      <TransactionForm
        v-if="isFormModalOpen"
        :initial-data="selectedTransaction"
        :transaction-type="modalType"
        @close="closeFormModal"
        @submit="handleFormSubmit"
      />
    </Modal>

     <ConfirmationModal
      v-if="transactionToDelete"
      :show="isDeleteModalOpen"
      title="Confirmar Eliminación"
      confirm-text="Sí, Eliminar"
      @close="closeDeleteModal"
      @confirm="confirmDelete"
    >
      <p class="text-gray-graphite">
        ¿Estás seguro de que quieres eliminar este registro?
        <br />
        <strong class="font-bold text-magenta-vibrant">"{{ transactionToDelete.description }}"</strong>
      </p>
    </ConfirmationModal>
  </div>
</template>

<script setup>
import { onMounted, ref, computed, watch } from 'vue';
import { useFinanceStore } from '../stores/finance';
import { storeToRefs } from 'pinia';
import { format } from 'date-fns';
import DataTable from '../components/DataTable.vue';
import Modal from '../components/Modal.vue';
import TransactionForm from '../components/TransactionForm.vue';
import ConfirmationModal from '../components/ConfirmationModal.vue';

const financeStore = useFinanceStore();
const {
  incomes, incomesPagination, isLoadingIncomes, incomesOrdering,
  expenses, expensesPagination, isLoadingExpenses, expensesOrdering
} = storeToRefs(financeStore);

const isFormModalOpen = ref(false);
const modalMode = ref('create');
const modalType = ref('income');
const selectedTransaction = ref(null);
const isDeleteModalOpen = ref(false);
const transactionToDelete = ref(null);
const incomeSearchQuery = ref('');
const expenseSearchQuery = ref('');

let incomeDebounceTimer = null;
watch(incomeSearchQuery, (newQuery) => {
  clearTimeout(incomeDebounceTimer);
  incomeDebounceTimer = setTimeout(() => {
    financeStore.setIncomesSearchTerm(newQuery);
  }, 300);
});

let expenseDebounceTimer = null;
watch(expenseSearchQuery, (newQuery) => {
  clearTimeout(expenseDebounceTimer);
  expenseDebounceTimer = setTimeout(() => {
    financeStore.setExpensesSearchTerm(newQuery);
  }, 300);
});

const modalTitle = computed(() => {
  const action = modalMode.value === 'create' ? 'Añadir' : 'Editar';
  const type = modalType.value === 'income' ? 'Ingreso' : 'Gasto';
  return `${action} ${type}`;
});

const incomeColumns = [
  { key: 'description', label: 'Descripción' },
  { key: 'amount', label: 'Monto' },
  { key: 'date', label: 'Fecha', sortable: true },
  { key: 'actions', label: 'Acciones', cellClass: 'text-right w-px whitespace-nowrap' },
];
const expenseColumns = [...incomeColumns];

const currentIncomeSortState = computed(() => {
  if (incomesOrdering.value.startsWith('-')) { return { key: incomesOrdering.value.substring(1), direction: 'desc' }; }
  if (incomesOrdering.value) { return { key: incomesOrdering.value, direction: 'asc' }; }
  return { key: '', direction: '' };
});
const currentExpenseSortState = computed(() => {
  if (expensesOrdering.value.startsWith('-')) { return { key: expensesOrdering.value.substring(1), direction: 'desc' }; }
  if (expensesOrdering.value) { return { key: expensesOrdering.value, direction: 'asc' }; }
  return { key: '', direction: '' };
});

const handleIncomePageChange = (newPage) => { financeStore.fetchIncomes(newPage); };
const handleExpensePageChange = (newPage) => { financeStore.fetchExpenses(newPage); };
const openModal = (type, mode, transaction = null) => {
  modalType.value = type;
  modalMode.value = mode;
  selectedTransaction.value = transaction ? { ...transaction } : { description: '', amount: '', date: new Date().toISOString().slice(0, 10) };
  isFormModalOpen.value = true;
};
const closeFormModal = () => { isFormModalOpen.value = false; selectedTransaction.value = null; };
const handleFormSubmit = (formData) => {
  if (modalType.value === 'income') {
    if (modalMode.value === 'create') { financeStore.createIncome(formData); }
    else { financeStore.updateIncome(selectedTransaction.value.id, formData); }
  } else {
    if (modalMode.value === 'create') { financeStore.createExpense(formData); }
    else { financeStore.updateExpense(selectedTransaction.value.id, formData); }
  }
  closeFormModal();
};
const openDeleteModal = (type, transaction) => {
  modalType.value = type;
  transactionToDelete.value = transaction;
  isDeleteModalOpen.value = true;
};
const closeDeleteModal = () => { isDeleteModalOpen.value = false; transactionToDelete.value = null; };
const confirmDelete = () => {
  if (modalType.value === 'income') { financeStore.deleteIncome(transactionToDelete.value.id); }
  else { financeStore.deleteExpense(transactionToDelete.value.id); }
  closeDeleteModal();
};

onMounted(() => {
  financeStore.fetchIncomes();
  financeStore.fetchExpenses();
});
</script>