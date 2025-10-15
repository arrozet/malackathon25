import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react({
      babel: {
        plugins: [['babel-plugin-react-compiler']],
      },
    }),
  ],
  // Server configuration for development and production
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    // Allow access from any host in production
    allowedHosts: [
      'localhost',
      '127.0.0.1',
      '158.179.212.221',
      'dr-artificial.com',
      'www.dr-artificial.com',
      '.dr-artificial.com', // Wildcard for all subdomains
    ],
    // Proxy de desarrollo: permite que el front consuma /api sin Nginx
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
  preview: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
  },
})
