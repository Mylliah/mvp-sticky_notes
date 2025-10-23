import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Configuration Vite
export default defineConfig({
  plugins: [react()],           // Active le plugin React
  server: {
    host: '0.0.0.0',            // Accessible depuis Docker
    port: 3000,                 // Port du serveur de dev
    watch: {
      usePolling: true          // Nécessaire pour Docker (détecte les changements)
    }
  }
})
