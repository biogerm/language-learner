import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import r2ProxyPlugin from './vite-plugin-r2.ts'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), r2ProxyPlugin()],
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('react')) return 'react-vendor';
            if (id.includes('@supabase')) return 'supabase-vendor';
            if (id.includes('dexie')) return 'dexie-vendor';
            return 'vendor';
          }
        }
      }
    }
  }
})
