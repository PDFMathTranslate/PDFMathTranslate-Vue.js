import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/v1': {
        target: 'http://localhost:11008',
        changeOrigin: true,
      },
    },
  },
})


