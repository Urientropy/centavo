// frontend/vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],

  base: '/static/',

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