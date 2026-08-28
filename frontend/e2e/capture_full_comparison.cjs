const { chromium } = require('playwright');
const path = require('path');

const ARTIFACT_DIR = './reports/a5d1ee7a-3f21-4b48-8371-19932f1e650d';

async function run() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1000, height: 850 } });
  const page = await context.newPage();

  // Login
  await page.goto('http://localhost:5173/login');
  await page.fill('input[type="email"]', 'test@example.com');
  await page.fill('input[type="password"]', 'test_password_placeholder');
  await page.click('button[type="submit"]');
  await page.waitForTimeout(1500);

  // 1. Study Dictation
  await page.goto('http://localhost:5173/dictation/sfid');
  await page.waitForTimeout(1500);
  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'dictation_study_interface.png') });

  // 2. Review Dictation
  const dReviewToggle = await page.$('#fsrs-mode-toggle button:has-text("Review")');
  if (dReviewToggle) await dReviewToggle.click();
  await page.waitForTimeout(1500);
  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'dictation_review_interface.png') });

  // 3. Study Flashcard
  await page.goto('http://localhost:5173/flashcard/sfid');
  await page.waitForTimeout(1500);
  const fStudyToggle = await page.$('#fsrs-mode-toggle button:has-text("Study")');
  if (fStudyToggle) await fStudyToggle.click();
  await page.waitForTimeout(1500);
  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'flashcard_study_interface.png') });

  // 4. Review Flashcard
  const fReviewToggle = await page.$('#fsrs-mode-toggle button:has-text("Review")');
  if (fReviewToggle) await fReviewToggle.click();
  await page.waitForTimeout(1500);
  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'flashcard_review_interface.png') });

  console.log('All full comparisons captured successfully!');
  await browser.close();
}

run().catch(console.error);
