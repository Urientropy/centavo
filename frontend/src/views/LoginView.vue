<template>
  <div class="min-h-screen bg-white-cloud flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <div class="text-center mb-12">
        <Logo class="h-20 w-auto inline-block text-indigo-electric" />
        <h1 class="font-display font-extrabold text-3xl text-gray-graphite mt-4">
          Bienvenido de vuelta
        </h1>
        <p class="text-gray-graphite/80 mt-1">
          Inicia sesión para continuar.
        </p>
      </div>

      <div class="bg-white p-8 rounded-lg border-2 border-gray-graphite shadow-[8px_8px_0px_#1F2937]">
        <div v-if="globalError" class="bg-magenta-vibrant/10 text-magenta-vibrant text-sm font-bold p-3 rounded-md mb-6 text-center">
          {{ globalError }}
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-6" autocomplete="off">
          <div>
            <label for="email" class="block font-bold text-sm text-gray-graphite mb-2">Correo Electrónico</label>
            <input
              type="email"
              id="email"
              v-model="formData.email"
              required
              autocomplete="off"
              :readonly="!emailFocused"
              @focus="emailFocused = true"
              class="w-full px-4 py-2 border-2 border-gray-graphite rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-energetic transition"
            >
            <span v-if="fieldErrors.email" class="text-magenta-vibrant text-xs mt-1">{{ fieldErrors.email[0] }}</span>
          </div>
          <div>
            <label for="password" class="block font-bold text-sm text-gray-graphite mb-2">Contraseña</label>
            <input
              type="password"
              id="password"
              v-model="formData.password"
              required
              autocomplete="new-password"
              :readonly="!passwordFocused"
              @focus="passwordFocused = true"
              class="w-full px-4 py-2 border-2 border-gray-graphite rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-energetic transition"
            >
            <span v-if="fieldErrors.password" class="text-magenta-vibrant text-xs mt-1">{{ fieldErrors.password[0] }}</span>
          </div>
          <button
            type="submit"
            :disabled="isLoading"
            class="w-full bg-indigo-electric text-white font-bold py-3 px-4 rounded-md border-2 border-gray-graphite shadow-[4px_4px_0px_#1F2937] hover:shadow-[2px_2px_0px_#1F2937] active:translate-x-[2px] active:translate-y-[2px] active:shadow-none transition-all disabled:bg-gray-400 disabled:shadow-none disabled:cursor-not-allowed"
          >
            <span v-if="isLoading">Ingresando...</span>
            <span v-else>Iniciar Sesión</span>
          </button>
        </form>

        <div class="text-center mt-6">
            <p class="text-sm text-gray-graphite">
                ¿No tienes una cuenta?
                <router-link :to="{ name: 'Register' }" class="font-bold text-indigo-electric hover:underline">
                    Regístrate aquí
                </router-link>
            </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useAuthStore } from '../stores/auth';
import Logo from '../components/Logo.vue';

const emailFocused = ref(false);
const passwordFocused = ref(false);

const authStore = useAuthStore();
const formData = reactive({ email: '', password: '' });
const isLoading = ref(false);
const globalError = ref(null);
const fieldErrors = ref({});

const handleSubmit = async () => {
  isLoading.value = true;
  globalError.value = null;
  fieldErrors.value = {};

  try {
    await authStore.login(formData);
  } catch (error) {
    if (error.response) {
      const status = error.response.status;
      const data = error.response.data;
      if (status === 401) {
        globalError.value = data.detail || "Correo electrónico o contraseña incorrectos.";
      } else if (status === 400) {
        fieldErrors.value = data;
      } else {
        globalError.value = "Ocurrió un error inesperado. Inténtalo de nuevo.";
      }
    } else {
      globalError.value = "No se pudo conectar con el servidor. Revisa tu conexión.";
    }
    console.error("Error de login:", error);
  } finally {
    isLoading.value = false;
  }
};
</script>