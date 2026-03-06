import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Navigation', () => {
  test('loads the canvas page', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('#top-nav')).toBeVisible();
  });

  test('top navigation shows Scaffold AI title', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByText('Scaffold AI').first()).toBeVisible();
  });

  test('split panel AI assistant is visible', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByText('AI Assistant')).toBeVisible();
  });

  test('has no accessibility violations', async ({ page }) => {
    await page.goto('/');
    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa'])
      .analyze();
    expect(results.violations).toEqual([]);
  });
});
