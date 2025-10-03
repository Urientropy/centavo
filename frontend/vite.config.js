// frontend/vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],

  // --- EL ÚNICO CAMBIO ---
  // Cuando se construye para producción, la base debe ser una cadena vacía
  // para que todas las rutas sean relativas.
  base: '',

  server: {
    host: 'localhost',
    port: 5173,
    hmr: {
      host: 'localhost'
    }
  },

  build: {
    outDir: './dist',
    manifest: true,
    rollupOptions: {
      input: 'src/main.js',
    },
  },
})