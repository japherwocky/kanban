import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import tailwindcss from '@tailwindcss/vite'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [svelte(), tailwindcss()],
  resolve: {
    alias: {
      '$lib': fileURLToPath(new URL('./src/lib', import.meta.url))
    },
    // Under vitest, svelte otherwise resolves to its server build and any
    // component render fails with "mount(...) is not available on the server".
    // Scoped to VITEST so the production build keeps its normal resolution.
    ...(process.env.VITEST ? { conditions: ['browser'] } : {}),
  },
  base: process.env.NODE_ENV === 'production' ? '/static/' : '/',
  build: {
    outDir: '../backend/static',
    emptyOutDir: true
  },
  // Vitest reads this file too. jsdom because the units under test touch
  // localStorage, document.documentElement and window.location.
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.js'],
    include: ['src/**/*.test.js'],
  },
  server: {
    // Not 8080: that is the backend's own default (manage.py --port), so the
    // dev server and the thing it proxies to were fighting for one port.
    // Matches .claude/launch.json.
    port: 5190,
    historyApiFallback: true,
    // All of these targeted :8000, which nothing listens on -- the backend
    // defaults to :8080. The dev proxy has therefore never reached the API.
    proxy: {
      '/api': 'http://localhost:8080',
      '/static': 'http://localhost:8080',
      '/content': 'http://localhost:8080',
      // The docs markdown lives at repo-root docs/, outside vite's root, so
      // vite cannot serve it and its SPA fallback answers /docs/<x>.md with
      // index.html instead. Docs.svelte then hands that HTML to marked and
      // renders the dev server's own <meta>/<script> tags as page content --
      // no error, no failed request, just a wrong-looking page.
      //
      // The backend already splits these correctly (docs_handler in
      // backend/main.py: .md serves the file, clean URLs serve the SPA), which
      // is the same split nginx does in production, so proxying is enough.
      // Requires the backend on :8080, exactly as /api already does.
      '/docs': 'http://localhost:8080'
    }
  }
})
