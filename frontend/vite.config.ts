import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    strictPort: true,
    proxy: Object.fromEntries(
      ['/api', '/openapi.json', '/docs'].map((path) => [
        path,
        process.env.YUANHANG_API_URL || 'http://127.0.0.1:8000',
      ]),
    ),
  },
  build: {
    outDir: process.env.YUANHANG_BUILD_DIR || 'dist',
    chunkSizeWarningLimit: 1500,
    rollupOptions: {
      output: {
        manualChunks: (id) =>
          id.includes('maplibre-gl')
            ? 'map'
            : id.includes('echarts')
              ? 'charts'
              : id.includes('node_modules/react')
                ? 'react'
                : undefined,
      },
    },
  },
})
