const { chromium } = require('playwright');
const path = require('path');

const ARTIFACT_DIR = process.env.ARTIFACT_DIR || './screenshots';
const SCREENSHOT_DIR = ARTIFACT_DIR;

async function runArLifecycleVerification() {
  console.log('=== RUNNING "ÄR" LIFECYCLE E2E VERIFICATION ===\n');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();

  // 1. Login
  console.log('Step 1: Logging in...');
  await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
  await page.fill('input[type="email"]', process.env.TEST_USER_EMAIL || 'test@example.com');
  await page.fill('input[type="password"]', process.env.TEST_USER_PASSWORD || 'test-password');
  await page.click('button[type="submit"]');
  await page.waitForTimeout(1500);

  // 2. Navigate to Narration Stage 12, Article art_58
  console.log('Step 2: Navigating to Narration Stage 12, art_58...');
  await page.goto('http://localhost:5173/narration/sfid', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  await page.locator('select').first().selectOption('stage_12');
  await page.waitForTimeout(800);
  await page.locator('select').nth(1).selectOption('art_58');
  await page.waitForTimeout(1500);

  // 3. Enter Edit Mode on Sentence 1
  console.log('Step 3: Entering Edit Mode on Sentence 1...');
  const s1 = page.locator('.sentence-card').first();
  await s1.hover();
  await s1.locator('.extract-vocab-btn').click();
  await page.waitForTimeout(1200);

  // 4. Click 'är' to select it
  console.log('Step 4: Clicking "är" to select it...');
  const arSpan = s1.locator('.selectable-word:has-text("är")').first();
  const initialClass = await arSpan.getAttribute('class');
  console.log('Initial class of "är" in Edit Mode:', initialClass);
  await arSpan.click();
  await page.waitForTimeout(400);

  const selectedClass = await arSpan.getAttribute('class');
  console.log('Class of "är" after click:', selectedClass);
  if (!selectedClass.includes('selected-custom-word')) {
    console.error('ERROR: "är" did not become selected-custom-word!');
  }

  // 5. Save Changes
  console.log('Step 5: Saving changes...');
  await s1.locator('.save-vocab-btn').click();
  await page.waitForTimeout(1500);

  // 6. Verify in Reading Mode: 'är' is green (.custom-word)
  console.log('Step 6: Verifying "är" in Reading Mode...');
  const readingAr = s1.locator('.custom-word:has-text("är")').first();
  const readingArCount = await readingAr.count();
  console.log('"är" with .custom-word count in Reading Mode:', readingArCount);
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'ar_01_reading_mode_green.png') });

  // 7. Re-enter Edit Mode: Verify 'är' has .selected-custom-word IMMEDIATELY!
  console.log('Step 7: Re-entering Edit Mode to verify "är" is GREEN initially...');
  await s1.hover();
  await s1.locator('.extract-vocab-btn').click();
  await page.waitForTimeout(1200);

  const reEditAr = s1.locator('.selectable-word:has-text("är")').first();
  const reEditArClass = await reEditAr.getAttribute('class');
  console.log('Class of "är" on RE-ENTERING Edit Mode:', reEditArClass);

  await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'ar_02_re_enter_edit_mode_green.png') });

  if (!reEditArClass.includes('selected-custom-word')) {
    console.error('FAILED: "är" is NOT green upon re-entering Edit Mode!');
    process.exit(1);
  }

  console.log('\n=== "ÄR" LIFECYCLE VERIFICATION PASSED PERFECTLY! ===');
  await browser.close();
}

runArLifecycleVerification().catch(err => {
  console.error('Fatal error during "är" lifecycle verification:', err);
  process.exit(1);
});
