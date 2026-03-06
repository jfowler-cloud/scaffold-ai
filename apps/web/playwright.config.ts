import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [['html', { open: 'never' }]],
  use: {
    baseURL: 'http://localhost:4173',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], channel: 'chrome' },
    },
  ],
  webServer: {
    command: 'node /home/user/Desktop/Projects/scaffold-ai/apps/web/node_modules/vite/bin/vite.js preview --port 4173 --host 127.0.0.1',
    url: 'http://localhost:4173/e2e.html',
    reuseExistingServer: true,
    timeout: 15000,
  },
})
