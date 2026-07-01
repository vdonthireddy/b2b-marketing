import { test, expect } from '@playwright/test';

test.describe('JourneyForge E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Log in before each test
    await page.goto('/login');
    await page.fill('input[name="email"]', 'admin');
    await page.fill('input[type="password"]', 'admin');
    await page.click('button:has-text("Sign in")');
    
    // Wait to land on dashboard
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('should navigate to dashboard and verify contents', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Dashboard');
    // Ensure stats cards exist (by checking for standard dashboard text)
    await expect(page.locator('text=Total Journeys')).toBeVisible();
    await expect(page.locator('text=Personas').first()).toBeVisible();
  });

  test('should navigate to journeys, create a new one, and enter builder', async ({ page }) => {
    // Go to Journeys
    await page.click('text=Journeys');
    await expect(page).toHaveURL(/\/journeys/);
    await expect(page.locator('h1')).toContainText('Journeys');

    // Create a new journey manually
    await page.locator('button:has-text("New Journey"), button:has-text("Create Journey")').first().click();
    
    // Check if the modal opened and fill it
    await expect(page.locator('text=Create New Journey')).toBeVisible();
    await page.fill('input[placeholder="e.g. Enterprise Onboarding"]', 'E2E Test Journey');
    await page.fill('textarea', 'This is an end-to-end test journey created by Playwright.');
    
    // Find the create button inside the modal/dialog
    const createBtn = page.locator('button', { hasText: 'Create' }).nth(1); // Usually the second one, or use specific selector if known
    
    // Wait for response after creation
    const responsePromise = page.waitForResponse(response => 
      response.url().includes('/api/journeys') && response.request().method() === 'POST'
    );
    await page.locator('button[type="submit"]:has-text("Create Journey")').click();
    
    const response = await responsePromise;
    expect(response.status()).toBe(200); // Created
    
    // Wait to be redirected to the builder
    await expect(page).toHaveURL(/\/journeys\/.+/);


    // Add a new stage
    await page.getByTestId('add-stage-button').click({ force: true });
    
    // Wait for the new stage to appear in the DOM
    await expect(page.locator('input[value="New Stage"]')).toBeVisible();
    
    // Click on the newly added stage (should be the last stage card)
    const newStageCard = page.getByTestId('stage-card').last();
    await newStageCard.click({ position: { x: 5, y: 5 } });
    
    // Ensure detail panel opens
    await expect(page.locator('h3').filter({ hasText: 'New Stage' })).toBeVisible();
  });

  test('should navigate to personas', async ({ page }) => {
    // Go to Personas
    await page.click('text=Personas');
    await expect(page).toHaveURL(/\/personas/);
    await expect(page.locator('h1')).toContainText('Personas');
  });

  test('should navigate to leads and verify pagination', async ({ page }) => {
    // Go to Leads
    await page.click('text=Leads');
    await expect(page).toHaveURL(/\/leads/);
    await expect(page.locator('h1')).toContainText('Leads');
    
    // Check if leads table is visible
    await expect(page.locator('table')).toBeVisible();
    
    // Check if we show 20 leads at a time
    const rows = await page.locator('tbody tr').count();
    expect(rows).toBeLessThanOrEqual(20);
  });

  test('should render complex journey in visual flow mode', async ({ page }) => {
    // Go to Journeys
    await page.click('text=Journeys');
    await expect(page).toHaveURL(/\/journeys/);
    
    // Find the complex journey
    await page.click('text=Enterprise Lead Nurturing Flow');
    await expect(page).toHaveURL(/\/journeys\/.+/);

    // Verify SVG connection layer exists and contains paths
    const svgPaths = page.locator('svg path');
    await expect(svgPaths.first()).toBeVisible();

    // Verify diamond split node exists (indicated by the custom text or icon)
    await expect(page.locator('text=Split: Demo Requested?')).toBeVisible();
    
    // Verify wait node exists
    await expect(page.locator('text=Wait 7 Days')).toBeVisible();
  });

  test('should verify dashboard stats tiles link to correct pages', async ({ page }) => {
    // Check Total Journeys tile
    await page.click('text=Total Journeys');
    await expect(page).toHaveURL(/\/journeys/);
    
    // Go back to Dashboard
    await page.click('text=Dashboard');
    await expect(page).toHaveURL(/\/dashboard/);
    
    // Check Personas tile
    await page.click('text=Personas');
    await expect(page).toHaveURL(/\/personas/);
  });

  test('should generate a new journey using AI Journey builder', async ({ page }) => {
    // Intercept and mock the AI generation request to keep the test instant and deterministic
    await page.route('**/api/ai/generate-journey', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'mock-ai-journey-id',
          name: 'AI Developer Platform Onboarding',
          description: 'Auto-generated developer onboarding track',
          stages: []
        })
      });
    });

    // Go to Journeys
    await page.click('text=Journeys');
    await expect(page).toHaveURL(/\/journeys/);

    // Click Generate with AI
    await page.click('button:has-text("Generate with AI")');
    await expect(page.locator('text=Generate Journey with AI')).toBeVisible();

    // Fill prompt
    await page.fill('textarea#prompt', 'Create an onboarding journey for developer platforms.');

    // Click Generate
    await page.click('form button:has-text("Generate")');

    // Should wait to land on the generated journey page
    await expect(page).toHaveURL(/\/journeys\/mock-ai-journey-id/, { timeout: 10000 });
  });
});

test('should display error message on incorrect login credentials', async ({ page }) => {
  await page.goto('/login');
  await page.fill('input[name="email"]', 'wrong_user');
  await page.fill('input[type="password"]', 'wrong_password');
  await page.click('button:has-text("Sign in")');
  
  const errorBox = page.locator('text=Invalid email or password');
  await expect(errorBox).toBeVisible();
});
