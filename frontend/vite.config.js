// frontend/vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ command }) => ({
  plugins: [vue()],
  base: command === 'build' ? '/static/' : '/', // 👈 importante
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
}))
