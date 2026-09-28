import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  base: process.env.VITE_BASE_PATH || './',
  cacheDir: 'tmp/vite-cache',
  plugins: [vue()],
  server: {
    watch: {
      ignored: ['**/tmp/**', '**/dist/**'],
    },
  },
  build: {
    target: 'es2022',
    sourcemap: false,
  },
  test: {
    environment: 'jsdom',
    include: ['src/**/*.test.ts'],
  },
})
