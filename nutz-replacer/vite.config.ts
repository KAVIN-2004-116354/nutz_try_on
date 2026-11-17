import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: './',
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/outputs': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/studio': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/sample_assets': {
        target: 'http://127.0.0.1:8000/studio/assets',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/sample_assets/, '')
      }
    }
  }
})
