import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import LoginView from '../views/LoginView.vue';
import RegisterView from '../views/RegisterView.vue';
import BaseLayout from '../layouts/BaseLayout.vue';
import DashboardView from '../views/DashboardView.vue';
import InventoryView from '../views/InventoryView.vue';
import RawMaterialDetailView from '../views/RawMaterialDetailView.vue';
import ProductsView from '../views/ProductsView.vue';
import ProductDetailView from '../views/ProductDetailView.vue';
import ProductionView from '../views/ProductionView.vue';
import FinanceView from '../views/FinanceView.vue'; // <-- Nuevo import

const routes = [
  { path: '/', redirect: '/login' },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { publicOnly: true, title: 'Iniciar Sesión' }
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterView,
    meta: { publicOnly: true, title: 'Registro' }
  },
  {
    path: '/app',
    component: BaseLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: DashboardView,
        meta: { title: 'Dashboard' }
      },
      {
        path: 'inventory',
        name: 'Inventory',
        component: InventoryView,
        meta: { title: 'Inventario' }
      },
      {
        path: 'inventory/raw-materials/:id',
        name: 'RawMaterialDetail',
        component: RawMaterialDetailView,
        meta: { title: 'Detalle de Materia Prima' }
      },
      {
        path: 'products',
        name: 'Products',
        component: ProductsView,
        meta: { title: 'Productos' }
      },
      {
        path: 'products/:id',
        name: 'ProductDetail',
        component: ProductDetailView,
        meta: { title: 'Detalle de Producto' }
      },
      {
        path: 'production',
        name: 'Production',
        component: ProductionView,
        meta: { title: 'Producción' }
      },
      // --- INICIO: NUEVA RUTA DE FINANZAS ---
      {
        path: 'finance',
        name: 'Finance',
        component: FinanceView,
        meta: { title: 'Finanzas' }
      }
      // --- FIN: NUEVA RUTA DE FINANZAS ---
    ]
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  const isLoggedIn = authStore.isAuthenticated;

  if (to.meta.requiresAuth && !isLoggedIn) {
    next({ name: 'Login' });
  } else if (isLoggedIn && to.meta.publicOnly) {
    next({ name: 'Dashboard' });
  } else {
    next();
  }
});

export default router;