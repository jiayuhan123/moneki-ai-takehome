import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    strictPort: true,
    // 浏览器始终请求同源 /api；开发时由 Vite 转发，部署时可由 FastAPI
    // 或反向代理提供同一路径，因此前端没有硬编码某台开发电脑的地址。
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
