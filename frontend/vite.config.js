import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file from project root (..)
  const env = loadEnv(mode, process.cwd() + '/..', '');
  const backendUrl = env.VITE_BACKEND_URL || 'http://localhost:8000';

  console.log('Proxying /api to:', backendUrl);

  return {
    plugins: [react()],
    server: {
      port: 3000,
      proxy: {
        '/api': {
          target: backendUrl,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, '')
        }
      }
    }
  }
})
