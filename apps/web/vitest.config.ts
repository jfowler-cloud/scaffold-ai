import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./vitest.setup.ts'],
    exclude: ['e2e/**', 'node_modules/**'],
    coverage: {
      provider: 'istanbul',
      reporter: ['text', 'json', 'lcov'],
      include: ['src/**/*.{ts,tsx}', 'components/**/*.{ts,tsx}', 'lib/**/*.{ts,tsx}'],
      exclude: ['src/main.tsx'],
      thresholds: { lines: 65, branches: 60, functions: 60, statements: 65 },
    },
  },
  resolve: {
    alias: {
      '@/lib': path.resolve(__dirname, './lib'),
      '@/components': path.resolve(__dirname, './components'),
      '@': path.resolve(__dirname, './src'),
    },
  },
});
