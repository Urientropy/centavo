// frontend/vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ command }) => {
  return {
    plugins: [vue()],

    // --- CONFIGURACIÓN DE BASE ---
    // En producción ('build'), la base debe ser relativa para que Django/WhiteNoise
    // puedan manejar las rutas correctamente.
    // En desarrollo ('serve'), la dejamos por defecto.
    base: command === 'serve' ? '' : '/static/',

    // --- CONFIGURACIÓN DE BUILD ---
    build: {
      // El directorio de salida donde irán los archivos compilados
      outDir: './dist',
      // Borra el outDir antes de cada build para evitar archivos viejos
      emptyOutDir: true,

      // Genera el manifest.json que django-vite necesita
      manifest: true,

      rollupOptions: {
        // El punto de entrada de tu aplicación
        input: 'src/main.js',
      },
    },

    // --- CONFIGURACIÓN DEL SERVIDOR DE DESARROLLO ---
    server: {
      host: 'localhost',
      port: 5173,
    },
  }
})