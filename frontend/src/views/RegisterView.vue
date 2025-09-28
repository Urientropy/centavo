<template>
  <div class="min-h-screen bg-white-cloud flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <!-- Encabezado con logo y branding -->
      <div class="text-center mb-12">
        <Logo class="h-20 w-auto inline-block text-indigo-electric" />
        <h1 class="font-display font-extrabold text-3xl text-gray-graphite mt-4">
          Crea tu cuenta en Centavo
        </h1>
        <p class="text-gray-graphite/80 mt-1">
          Empieza a tomar el control de tus finanzas.
        </p>
      </div>

      <!-- Tarjeta del formulario con estilo neo-brutalista -->
      <div class="bg-white p-8 rounded-lg border-2 border-gray-graphite shadow-[8px_8px_0px_#1F2937]">
        <form @submit.prevent="handleSubmit" class="space-y-6" autocomplete="off">

          <div>
            <label for="tenant_name" class="block font-bold text-sm text-gray-graphite mb-2">
              Nombre de tu Negocio
            </label>
            <input
              type="text"
              id="tenant_name"
              v-model="formData.tenant_name"
              required
              autocomplete="off"
              class="w-full px-4 py-2 border-2 border-gray-graphite rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-energetic transition"
            >
            <span v-if="errors.tenant_name" class="text-magenta-vibrant text-xs mt-1">{{ errors.tenant_name[0] }}</span>
          </div>

          <div>
            <label for="first_name" class="block font-bold text-sm text-gray-graphite mb-2">Nombre</label>
            <input type="text" id="first_name" v-model="formData.first_name" required autocomplete="off" class="w-full px-4 py-2 border-2 border-gray-graphite rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-energetic transition">
            <span v-if="errors.first_name" class="text-magenta-vibrant text-xs mt-1">{{ errors.first_name[0] }}</span>
          </div>

          <div>
            <label for="last_name" class="block font-bold text-sm text-gray-graphite mb-2">Apellidos</label>
            <input type="text" id="last_name" v-model="formData.last_name" required autocomplete="off" class="w-full px-4 py-2 border-2 border-gray-graphite rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-energetic transition">
            <span v-if="errors.last_name" class="text-magenta-vibrant text-xs mt-1">{{ errors.last_name[0] }}</span>
          </div>

          <div>
            <label for="email" class="block font-bold text-sm text-gray-graphite mb-2">Correo Electrónico</label>
            <input type="email" id="email" v-model="formData.email" required autocomplete="off" class="w-full px-4 py-2 border-2 border-gray-graphite rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-energetic transition">
            <span v-if="errors.email" class="text-magenta-vibrant text-xs mt-1">{{ errors.email[0] }}</span>
          </div>

          <div>
            <label for="password" class="block font-bold text-sm text-gray-graphite mb-2">Contraseña</label>
            <input type="password" id="password" v-model="formData.password" required autocomplete="new-password" class="w-full px-4 py-2 border-2 border-gray-graphite rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-energetic transition">
            <span v-if="errors.password" class="text-magenta-vibrant text-xs mt-1">{{ errors.password[0] }}</span>
          </div>

          <!-- Botón de acción con efecto "pulsable" -->
          <button
            type="submit"
            :disabled="isLoading"
            class="w-full bg-indigo-electric text-white font-bold py-3 px-4 rounded-md border-2 border-gray-graphite shadow-[4px_4px_0px_#1F2937] hover:shadow-[2px_2px_0px_#1F2937] active:translate-x-[2px] active:translate-y-[2px] active:shadow-none transition-all disabled:bg-gray-400 disabled:shadow-none disabled:cursor-not-allowed"
          >
            <span v-if="isLoading">Creando cuenta...</span>
            <span v-else>Crear mi cuenta</span>
          </button>
        </form>

        <!-- SECCIÓN AÑADIDA -->
        <div class="text-center mt-6">
          <p class="text-sm text-gray-graphite">
            ¿Ya tienes una cuenta?
            <router-link :to="{ name: 'Login' }" class="font-bold text-indigo-electric hover:underline">
              Inicia sesión aquí
            </router-link>
          </p>
        </div>
        <!-- FIN SECCIÓN AÑADIDA -->

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useAuthStore } from '../stores/auth';
import Logo from '../components/Logo.vue';

const authStore = useAuthStore();

const formData = reactive({
  tenant_name: '',
  first_name: '',
  last_name: '',
  email: '',
  password: ''
});

const isLoading = ref(false);
const errors = ref({});

const handleSubmit = async () => {
  isLoading.value = true;
  errors.value = {};

  try {
    await authStore.register(formData);
    // La redirección ocurre dentro del store si es exitoso
  } catch (error) {
    // El store lanza el objeto de error del backend
    errors.value = error;
  } finally {
    isLoading.value = false;
  }
};
</script>