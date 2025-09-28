<template>
  <div class="w-full min-h-screen bg-white-cloud">
    <div v-if="isMobileMenuOpen" @click="isMobileMenuOpen = false" class="fixed inset-0 z-30 bg-black/40 backdrop-blur-sm lg:hidden"></div>

    <div class="relative lg:grid lg:grid-cols-[auto_1fr] lg:gap-8 lg:p-12 h-screen">
      <aside
        class="fixed inset-y-0 left-0 z-40 w-64 bg-white p-6 flex flex-col transform transition-transform duration-300 ease-in-out lg:static lg:transform-none lg:border-2 lg:border-gray-graphite lg:rounded-xl lg:shadow-[8px_8px_0px_#1F2937]"
        :class="{ 'translate-x-0': isMobileMenuOpen, '-translate-x-full': !isMobileMenuOpen }"
      >
        <div class="mb-12 flex justify-center">
          <router-link :to="{ name: 'Dashboard' }">
            <Logo class="h-14 w-auto text-indigo-electric hover:opacity-80 transition-opacity mt-4" />
          </router-link>
        </div>

        <nav>
          <ul class="flex flex-col gap-2">
            <li v-for="link in navigationLinks" :key="link.name">
              <router-link :to="{ name: link.routeName }" class="nav-link" @click="closeMobileMenu">
                <component :is="link.icon" class="h-6 w-6" />
                <span>{{ link.name }}</span>
              </router-link>
            </li>
          </ul>
        </nav>

        <div class="mt-auto">
          <button @click="handleLogout" class="logout-button">
            <ArrowLeftOnRectangleIcon class="h-6 w-6" />
            <span>Cerrar Sesión</span>
          </button>
        </div>
      </aside>

      <div class="flex flex-col w-full overflow-hidden">
        <header class="flex items-center justify-between p-4 bg-white border-b-2 border-gray-graphite lg:hidden">
          <button @click="isMobileMenuOpen = true" class="text-gray-graphite p-2 -ml-2">
            <Bars3Icon class="h-8 w-8" />
          </button>
          <span class="font-display font-bold text-xl">{{ currentRouteTitle }}</span>
          <router-link :to="{ name: 'Dashboard' }">
            <Logo class="h-8 w-auto text-indigo-electric" />
          </router-link>
        </header>
        <main class="flex-1 overflow-y-auto p-4 md:p-8">
          <router-view />
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRoute } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import Logo from '../components/Logo.vue';
import {
  ChartPieIcon,
  ArchiveBoxIcon,
  ArrowLeftOnRectangleIcon,
  Bars3Icon,
  CubeIcon,
  BuildingStorefrontIcon,
  ScaleIcon, // <-- NUEVO ICONO
} from '@heroicons/vue/24/outline';

const isMobileMenuOpen = ref(false);
const route = useRoute();
const authStore = useAuthStore();

const currentRouteTitle = computed(() => route.meta.title || 'Centavo');

const closeMobileMenu = () => {
  isMobileMenuOpen.value = false;
};

const handleLogout = () => {
  closeMobileMenu();
  authStore.logout();
};

const navigationLinks = [
  { name: 'Dashboard', routeName: 'Dashboard', icon: ChartPieIcon },
  { name: 'Inventario', routeName: 'Inventory', icon: ArchiveBoxIcon },
  { name: 'Productos', routeName: 'Products', icon: CubeIcon },
  { name: 'Producción', routeName: 'Production', icon: BuildingStorefrontIcon },
  { name: 'Finanzas', routeName: 'Finance', icon: ScaleIcon }, // <-- NUEVO ENLACE
];
</script>

<style scoped>
.nav-link {
  @apply flex items-center gap-4 w-full px-4 py-3 rounded-md
         font-display font-bold text-lg text-gray-graphite
         transition-colors duration-200;
}
.nav-link:not(.router-link-exact-active):hover {
  @apply bg-gray-graphite/5;
}
.nav-link.router-link-exact-active {
  @apply bg-indigo-electric text-white;
}
.logout-button {
  @apply flex items-center gap-4 w-full px-4 py-3 rounded-md
         font-display font-bold text-lg text-gray-graphite
         transition-colors duration-200;
}
.logout-button:hover {
  @apply bg-magenta-vibrant/10 text-magenta-vibrant;
}
</style>