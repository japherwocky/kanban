import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import tailwindcss from '@tailwindcss/vite'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [svelte(), tailwindcss()],
  resolve: {
    alias: {
      '$lib': fileURLToPath(new URL('./src/lib', import.meta.url))
    }
  },
  base: process.env.NODE_ENV === 'production' ? '/static/' : '/',
  build: {
    outDir: '../backend/static',
    emptyOutDir: true
  },
  server: {
    port: 8080,
    historyApiFallback: true,
    proxy: {
      '/api': 'http://localhost:8000',
      '/static': 'http://localhost:8000',
      '/content': 'http://localhost:8000'
    }
  }
})
