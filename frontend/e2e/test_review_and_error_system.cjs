const { chromium } = require('playwright');
const path = require('path');

const ARTIFACT_DIR = './reports/a5d1ee7a-3f21-4b48-8371-19932f1e650d';

async function run() {
  console.log('Starting Playwright test for error hint system and review mode UI...');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1000, height: 850 } });
  const page = await context.newPage();

  // Login
  await page.goto('http://localhost:5173/login');
  await page.fill('input[type="email"]', 'test@example.com');
  await page.fill('input[type="password"]', 'test_password_placeholder');
  await page.click('button[type="submit"]');
  await page.waitForTimeout(1500);

  // 1. Dictation - Testing Error Feedback
  console.log('--- Testing Dictation Error Feedback System ---');
  await page.goto('http://localhost:5173/dictation/sfid');
  await page.waitForTimeout(1500);

  // Too long
  await page.fill('#spell-input', 'thisiswaytoolongtext');
  await page.keyboard.press('Enter');
  await page.waitForTimeout(300);
  const fb1 = await page.$eval('#feedback-msg', el => el.textContent.trim());
  console.log('Feedback for too long:', fb1);
  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'dictation_too_long.png') });

  // Too short
  await page.fill('#spell-input', 'a');
  await page.keyboard.press('Enter');
  await page.waitForTimeout(300);
  const fb2 = await page.$eval('#feedback-msg', el => el.textContent.trim());
  console.log('Feedback for too short:', fb2);
  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'dictation_too_short_and_hint.png') });

  // 2. Flashcard - Testing Progressive Hints
  console.log('--- Testing Flashcard Progressive Hints ---');
  await page.goto('http://localhost:5173/flashcard/sfid');
  await page.waitForTimeout(1500);

  // Wrong 1
  await page.fill('#spell-input', 'wrong1');
  await page.keyboard.press('Enter');
  await page.waitForTimeout(300);

  // Wrong 2 (Should trigger audio hint button)
  await page.fill('#spell-input', 'wrong2');
  await page.keyboard.press('Enter');
  await page.waitForTimeout(300);
  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'flashcard_audio_hint.png') });

  // Wrong 3 (Should trigger context sentence masked hint)
  await page.fill('#spell-input', 'wrong3');
  await page.keyboard.press('Enter');
  await page.waitForTimeout(300);
  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'flashcard_context_hint.png') });

  // 3. Review Mode UI with FSRS Stats Panel
  console.log('--- Testing Review Mode UI with FSRS Stats ---');
  await page.goto('http://localhost:5173/dictation/sfid');
  await page.waitForTimeout(1000);
  const reviewToggle = await page.$('#fsrs-mode-toggle button:has-text("Review")');
  if (reviewToggle) await reviewToggle.click();
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'dictation_review_mode_stats.png') });

  await page.goto('http://localhost:5173/flashcard/sfid');
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'flashcard_review_mode_stats.png') });

  console.log('ALL ERROR FEEDBACK & REVIEW MODE UI TESTS COMPLETED!');
  await browser.close();
}

run().catch(console.error);
