// frontend/vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'


export default defineConfig({
  plugins: [vue()],

  // Base para desarrollo (debe ser la raíz '/')
  base: '/static/',

  // --- NUEVA SECCIÓN ---
  // Configuración explícita del servidor de desarrollo
  server: {
    // Aseguramos que Vite escuche en la dirección correcta
    host: 'localhost',
    port: 5173,
    // Necesario para el Hot Module Replacement (HMR)
    hmr: {
      host: 'localhost'
    }
  },
  // ---------------------

  build: {
    // Directorio de salida
    outDir: './dist',

    // Genera el manifest.json
    manifest: true,

    rollupOptions: {
      input: 'src/main.js',
    },
  },
})