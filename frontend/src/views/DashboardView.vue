<template>
  <div class="space-y-8">
    <div>
      <h1 class="font-display text-4xl font-extrabold text-gray-graphite">Dashboard Principal</h1>
      <p v-if="authStore.user" class="mt-1 text-lg text-gray-graphite/80">
        Aquí tienes un resumen del rendimiento de tu negocio, {{ authStore.user.first_name }}.
      </p>
    </div>

    <!-- SECCIÓN DE KPIs -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div v-for="kpi in kpis" :key="kpi.label" class="bg-white p-6 rounded-lg border-2 border-gray-graphite">
        <h3 class="font-display font-bold text-gray-graphite/70">{{ kpi.label }}</h3>
        <p class="font-display text-4xl font-extrabold" :class="kpi.colorClass">{{ kpi.value }}</p>
      </div>
    </div>

    <!-- SECCIÓN PRINCIPAL: Gráfico y Listas -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">

      <!-- Gráfico Principal -->
      <div class="lg:col-span-2 bg-white p-6 rounded-lg border-2 border-gray-graphite shadow-[8px_8px_0px_#1F2937]">
        <h3 class="font-display text-2xl font-bold text-gray-graphite mb-4">Ingresos vs. Gastos (Últimos 6 Meses)</h3>
        <div>
          <canvas id="incomeVsExpenseChart"></canvas>
        </div>
      </div>

      <!-- Widgets Laterales -->
      <div class="space-y-8">
        <!-- Productos Más Rentables -->
        <div class="bg-white p-6 rounded-lg border-2 border-gray-graphite">
          <h3 class="font-display text-xl font-bold text-gray-graphite mb-4">Productos Más Rentables</h3>
          <ul class="space-y-3">
            <li v-for="product in topProducts" :key="product.name" class="flex justify-between items-center">
              <span class="font-bold">{{ product.name }}</span>
              <span class="font-bold text-sm text-cyan-energetic bg-cyan-energetic/10 px-2 py-1 rounded-md">{{ product.profit }}</span>
            </li>
          </ul>
        </div>

        <!-- Materias Primas Bajas de Stock -->
        <div class="bg-white p-6 rounded-lg border-2 border-gray-graphite">
          <h3 class="font-display text-xl font-bold text-gray-graphite mb-4">Materias Primas Bajas de Stock</h3>
           <ul class="space-y-3">
            <li v-for="item in lowStockItems" :key="item.name" class="flex justify-between items-center">
              <span class="font-bold">{{ item.name }}</span>
              <span class="font-bold text-sm text-magenta-vibrant bg-magenta-vibrant/10 px-2 py-1 rounded-md">
                {{ item.stock }} {{ item.unit }}
              </span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useAuthStore } from '../stores/auth';

const authStore = useAuthStore();
let incomeVsExpenseChart = null;

// --- DATOS SIMULADOS ---
const kpis = ref([
  { label: 'Ingresos del Mes', value: 'C$ 45,800.50', colorClass: 'text-cyan-energetic' },
  { label: 'Gastos del Mes', value: 'C$ 22,150.00', colorClass: 'text-magenta-vibrant' },
  { label: 'Beneficio Neto', value: 'C$ 23,650.50', colorClass: 'text-indigo-electric' },
]);

const incomeVsExpenseChartData = {
  labels: ['Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep'],
  datasets: [
    {
      label: 'Ingresos',
      data: [35000, 42000, 55000, 48000, 60000, 45800],
      backgroundColor: '#06B6D4', // cyan-energetic
      borderColor: '#06B6D4',
      borderWidth: 2,
      borderRadius: 6,
    },
    {
      label: 'Gastos',
      data: [20000, 25000, 30000, 28000, 32000, 22150],
      backgroundColor: '#EC4899', // magenta-vibrant
      borderColor: '#EC4899',
      borderWidth: 2,
      borderRadius: 6,
    }
  ]
};

const topProducts = ref([
  { name: 'Torta de Chocolate', profit: 'C$ 12,500' },
  { name: 'Pan de Banano', profit: 'C$ 8,200' },
  { name: 'Galletas de Avena', profit: 'C$ 6,800' },
]);

const lowStockItems = ref([
  { name: 'Harina', stock: 5, unit: 'Libras' },
  { name: 'Huevos', stock: 12, unit: 'Unidades' },
  { name: 'Levadura', stock: 2, unit: 'Libras' },
]);
// ----------------------

const createChart = () => {
  if (incomeVsExpenseChart) {
    incomeVsExpenseChart.destroy();
  }
  const ctx = document.getElementById('incomeVsExpenseChart');
  if (!ctx) return;

  incomeVsExpenseChart = new Chart(ctx, {
    type: 'bar',
    data: incomeVsExpenseChartData,
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: 'top',
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function(value) {
              return 'C$ ' + value / 1000 + 'k';
            }
          }
        }
      }
    }
  });
};

onMounted(() => {
  createChart();
});

onUnmounted(() => {
  if (incomeVsExpenseChart) {
    incomeVsExpenseChart.destroy();
  }
});
</script>