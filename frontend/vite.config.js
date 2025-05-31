import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: { // Optional: configuration for dev server
    port: 3000, // Example port
    proxy: { // Example: proxy API requests to backend
      '/api': {
        target: 'http://localhost:8000', // Assuming backend runs on 8000
        changeOrigin: true,
        // rewrite: (path) => path.replace(/^\/api/, '') // if backend doesn't have /api prefix
      }
    }
  }
})
