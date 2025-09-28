import { defineStore } from 'pinia';
import apiClient from '../services/api';

export const useFinanceStore = defineStore('finance', {
  state: () => ({
    // Estado para Ingresos
    incomes: [],
    incomesPagination: { count: 0, page: 1, totalPages: 1 },
    isLoadingIncomes: false,
    incomesOrdering: '-date',
    incomesSearchTerm: '',

    // Estado para Gastos
    expenses: [],
    expensesPagination: { count: 0, page: 1, totalPages: 1 },
    isLoadingExpenses: false,
    expensesOrdering: '-date',
    expensesSearchTerm: '',

    error: null,
  }),
  actions: {
    // --- ACCIONES PARA INGRESOS ---
    async fetchIncomes(page = 1) {
      this.isLoadingIncomes = true;
      this.error = null;
      const params = new URLSearchParams();
      params.append('page', page);
      if (this.incomesSearchTerm.trim()) { params.append('search', this.incomesSearchTerm.trim()); }
      if (this.incomesOrdering) { params.append('ordering', this.incomesOrdering); }

      try {
        const response = await apiClient.get(`/finance/incomes/?${params.toString()}`);
        this.incomes = response.data.results;
        this.incomesPagination.count = response.data.count;
        this.incomesPagination.page = page;
        this.incomesPagination.totalPages = Math.ceil(response.data.count / 6);
      } catch (error) {
        this.error = "No se pudieron cargar los ingresos.";
        console.error("Error al obtener ingresos:", error);
      } finally {
        this.isLoadingIncomes = false;
      }
    },
    setIncomesOrdering(columnKey) {
      if (this.incomesOrdering === columnKey) { this.incomesOrdering = `-${columnKey}`; }
      else if (this.incomesOrdering === `-${columnKey}`) { this.incomesOrdering = ''; }
      else { this.incomesOrdering = columnKey; }
      this.fetchIncomes(1);
    },
    setIncomesSearchTerm(term) {
      this.incomesSearchTerm = term;
      this.fetchIncomes(1);
    },
    async createIncome(payload) {
      try {
        await apiClient.post('/finance/incomes/', payload);
        await this.fetchIncomes(1);
      } catch (error) { console.error("Error al crear ingreso:", error); throw error; }
    },
    async updateIncome(id, payload) {
      try {
        await apiClient.patch(`/finance/incomes/${id}/`, payload);
        await this.fetchIncomes(this.incomesPagination.page);
      } catch (error) { console.error("Error al actualizar ingreso:", error); throw error; }
    },
    async deleteIncome(id) {
      try {
        await apiClient.delete(`/finance/incomes/${id}/`);
        await this.fetchIncomes(this.incomesPagination.page);
      } catch (error) { console.error("Error al eliminar ingreso:", error); throw error; }
    },

    // --- ACCIONES PARA GASTOS ---
    async fetchExpenses(page = 1) {
      this.isLoadingExpenses = true;
      this.error = null;
      const params = new URLSearchParams();
      params.append('page', page);
      if (this.expensesSearchTerm.trim()) { params.append('search', this.expensesSearchTerm.trim()); }
      if (this.expensesOrdering) { params.append('ordering', this.expensesOrdering); }

      try {
        const response = await apiClient.get(`/finance/expenses/?${params.toString()}`);
        this.expenses = response.data.results;
        this.expensesPagination.count = response.data.count;
        this.expensesPagination.page = page;
        this.expensesPagination.totalPages = Math.ceil(response.data.count / 6);
      } catch (error) {
        this.error = "No se pudieron cargar los gastos.";
        console.error("Error al obtener gastos:", error);
      } finally {
        this.isLoadingExpenses = false;
      }
    },
    setExpensesOrdering(columnKey) {
      if (this.expensesOrdering === columnKey) { this.expensesOrdering = `-${columnKey}`; }
      else if (this.expensesOrdering === `-${columnKey}`) { this.expensesOrdering = ''; }
      else { this.expensesOrdering = columnKey; }
      this.fetchExpenses(1);
    },
    setExpensesSearchTerm(term) {
      this.expensesSearchTerm = term;
      this.fetchExpenses(1);
    },
    async createExpense(payload) {
      try {
        await apiClient.post('/finance/expenses/', payload);
        await this.fetchExpenses(1);
      } catch (error) { console.error("Error al crear gasto:", error); throw error; }
    },
    async updateExpense(id, payload) {
      try {
        await apiClient.patch(`/finance/expenses/${id}/`, payload);
        await this.fetchExpenses(this.expensesPagination.page);
      } catch (error) { console.error("Error al actualizar gasto:", error); throw error; }
    },
    async deleteExpense(id) {
      try {
        await apiClient.delete(`/finance/expenses/${id}/`);
        await this.fetchExpenses(this.expensesPagination.page);
      } catch (error) { console.error("Error al eliminar gasto:", error); throw error; }
    },
  },
});