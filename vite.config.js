import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    watch: {
      ignored: ['**/.venv/**', '**/backend/**', '**/dl/**', '**/__pycache__/**', '**/temp/**', '**/saved_model/**']
    }
  }
})
