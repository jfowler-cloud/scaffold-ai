import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig(({ mode }) => ({
  plugins: [react()],
  resolve: {
    alias: {
      ...(mode === 'e2e' ? { 'aws-amplify/auth': path.resolve(__dirname, 'src/test/e2e-auth-stub.ts') } : {}),
      '@/lib': path.resolve(__dirname, './lib'),
      '@/components': path.resolve(__dirname, './components'),
      '@': path.resolve(__dirname, './src'),
    },
  },
  ...(mode === 'e2e' ? {
    build: {
      rollupOptions: {
        input: { index: 'e2e.html' },
        output: {
          entryFileNames: 'assets/[name]-[hash].js',
        },
      },
    },
  } : {}),
}))
