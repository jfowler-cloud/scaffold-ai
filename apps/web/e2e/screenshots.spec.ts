/**
 * Screenshot capture spec — generates docs/images/ for the README.
 * Run with: npx playwright test e2e/screenshots.spec.ts
 */
import { test } from '@playwright/test'
import { mockAuth, mockAWS } from './helpers'

const OUT = '/home/user/Desktop/Projects/scaffold-ai/docs/images'

const POPULATED_GRAPH = {
  updated_graph: {
    nodes: [
      { id: 'frontend-1', type: 'frontend', position: { x: 100, y: 200 }, data: { label: 'React Frontend', type: 'frontend' } },
      { id: 'api-1', type: 'api', position: { x: 350, y: 200 }, data: { label: 'API Gateway', type: 'api' } },
      { id: 'lambda-1', type: 'lambda', position: { x: 600, y: 100 }, data: { label: 'Auth Lambda', type: 'lambda' } },
      { id: 'lambda-2', type: 'lambda', position: { x: 600, y: 300 }, data: { label: 'Data Lambda', type: 'lambda' } },
      { id: 'auth-1', type: 'auth', position: { x: 850, y: 100 }, data: { label: 'Cognito', type: 'auth' } },
      { id: 'db-1', type: 'database', position: { x: 850, y: 300 }, data: { label: 'DynamoDB', type: 'database' } },
    ],
    edges: [
      { id: 'e1', source: 'frontend-1', target: 'api-1' },
      { id: 'e2', source: 'api-1', target: 'lambda-1' },
      { id: 'e3', source: 'api-1', target: 'lambda-2' },
      { id: 'e4', source: 'lambda-1', target: 'auth-1' },
      { id: 'e5', source: 'lambda-2', target: 'db-1' },
    ],
  },
  message: 'Here is a serverless architecture for your app.',
}

test.use({ viewport: { width: 1600, height: 900 } })

test('01 - blank canvas', async ({ page }) => {
  await mockAuth(page)
  await mockAWS(page)
  await page.route('**/api/chat', route => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(POPULATED_GRAPH) }))
  await page.goto('/e2e.html')
  await page.waitForSelector('#top-nav', { timeout: 8000 })
  await page.waitForTimeout(500)
  await page.screenshot({ path: `${OUT}/blank_canvas.png`, fullPage: false })
})

test('02 - populated canvas', async ({ page }) => {
  await mockAuth(page)
  await mockAWS(page)
  await page.route('**/api/chat', route => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(POPULATED_GRAPH) }))
  await page.goto('/e2e.html')
  await page.waitForSelector('#top-nav', { timeout: 8000 })

  // Type a message and submit to populate the canvas
  await page.locator('textarea, input[type="text"]').last().fill('Build a serverless web app with auth and a database')
  await page.keyboard.press('Enter')
  await page.waitForTimeout(1000)
  await page.screenshot({ path: `${OUT}/populate_canvas.png`, fullPage: false })
})
