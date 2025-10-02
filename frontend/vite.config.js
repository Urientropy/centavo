// frontend/vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],

  // --- EL ÚNICO CAMBIO ---
  // Cuando se construye para producción, asegúrate de que
  // la base de los assets empiece con /static/
  base: process.env.NODE_ENV === 'production' ? '/static/' : '/',

  build: {
    outDir: './dist',
    manifest: true,
    rollupOptions: {
      input: 'src/main.js',
    },
  },
})