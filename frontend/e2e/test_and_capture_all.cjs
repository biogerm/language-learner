const { chromium } = require('playwright');
const path = require('path');

const ARTIFACT_DIR = process.env.ARTIFACT_DIR || './screenshots';
const SCREENSHOT_DIR = ARTIFACT_DIR;

async function run() {
  console.log('Starting Playwright test run with domcontentloaded...');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1000, height: 800 } });
  
  // 1. Legacy Dictation
  const pageL = await context.newPage();
  await pageL.goto('http://127.0.0.1:8000/dictation.html', { waitUntil: 'domcontentloaded' });
  await pageL.evaluate(() => {
    localStorage.setItem('sharedCourse', 'sfid');
    localStorage.setItem('appMode', 'study');
  });
  await pageL.goto('http://127.0.0.1:8000/dictation.html', { waitUntil: 'domcontentloaded' });
  await pageL.waitForTimeout(500);
  await pageL.selectOption('#stage-select', 'stage_01').catch(() => {});
  await pageL.waitForTimeout(200);
  await pageL.selectOption('#article-select', 'art_00').catch(() => {});
  await pageL.waitForTimeout(500);
  await pageL.screenshot({ path: path.join(ARTIFACT_DIR, 'legacy_dictation_study.png') });
  console.log('Saved legacy_dictation_study.png');

  // 2. Legacy Flashcard
  await pageL.goto('http://127.0.0.1:8000/flashcard.html', { waitUntil: 'domcontentloaded' });
  await pageL.evaluate(() => {
    localStorage.setItem('sharedCourse', 'sfid');
    localStorage.setItem('appMode', 'study');
  });
  await pageL.goto('http://127.0.0.1:8000/flashcard.html', { waitUntil: 'domcontentloaded' });
  await pageL.waitForTimeout(500);
  await pageL.selectOption('#stage-select', 'stage_01').catch(() => {});
  await pageL.waitForTimeout(200);
  await pageL.selectOption('#article-select', 'art_00').catch(() => {});
  await pageL.waitForTimeout(500);
  await pageL.screenshot({ path: path.join(ARTIFACT_DIR, 'legacy_flashcard_study.png') });
  console.log('Saved legacy_flashcard_study.png');
  await pageL.close();

  // 3. Cloud App
  const pageC = await context.newPage();
  await pageC.goto('http://127.0.0.1:5173/login', { waitUntil: 'domcontentloaded' });
  await pageC.waitForSelector('input[type="email"]', { timeout: 5000 });
  await pageC.fill('input[type="email"]', 'test@example.com');
  await pageC.fill('input[type="password"]', process.env.TEST_USER_PASSWORD || 'test-password');
  await pageC.click('button[type="submit"]');
  await pageC.waitForTimeout(1500);

  // Cloud Dictation - Initial
  await pageC.goto('http://127.0.0.1:5173/dictation/sfid', { waitUntil: 'domcontentloaded' });
  await pageC.waitForTimeout(1500);
  await pageC.selectOption('#stage-select', 'stage_01').catch(() => {});
  await pageC.waitForTimeout(300);
  await pageC.selectOption('#article-select', 'art_00').catch(() => {});
  await pageC.waitForTimeout(800);
  await pageC.screenshot({ path: path.join(ARTIFACT_DIR, 'cloud_dictation_study_initial.png') });
  console.log('Saved cloud_dictation_study_initial.png');

  // Cloud Dictation - Typing & Reveal
  await pageC.click('#spell-input');
  await pageC.type('#spell-input', 'testwrong');
  await pageC.keyboard.press('Enter');
  await pageC.waitForTimeout(300);
  await pageC.keyboard.press('Enter');
  await pageC.waitForTimeout(300);
  await pageC.keyboard.press('Enter');
  await pageC.waitForTimeout(300);
  await pageC.screenshot({ path: path.join(ARTIFACT_DIR, 'cloud_dictation_wrong_state.png') });
  console.log('Saved cloud_dictation_wrong_state.png');

  // Click Reveal Answer
  const revealBtn = await pageC.$('#reveal-btn');
  if (revealBtn) {
    await revealBtn.click();
    await pageC.waitForTimeout(400);
    await pageC.screenshot({ path: path.join(ARTIFACT_DIR, 'cloud_dictation_revealed_state.png') });
    console.log('Saved cloud_dictation_revealed_state.png');
  }

  // Cloud Flashcard - Initial
  await pageC.goto('http://127.0.0.1:5173/flashcard/sfid', { waitUntil: 'domcontentloaded' });
  await pageC.waitForTimeout(1500);
  await pageC.selectOption('#stage-select', 'stage_01').catch(() => {});
  await pageC.waitForTimeout(300);
  await pageC.selectOption('#article-select', 'art_00').catch(() => {});
  await pageC.waitForTimeout(800);
  await pageC.screenshot({ path: path.join(ARTIFACT_DIR, 'cloud_flashcard_study_initial.png') });
  console.log('Saved cloud_flashcard_study_initial.png');

  // Cloud Flashcard - Typing & Reveal
  await pageC.click('#spell-input');
  await pageC.type('#spell-input', 'wrongword');
  await pageC.keyboard.press('Enter');
  await pageC.waitForTimeout(300);
  await pageC.screenshot({ path: path.join(ARTIFACT_DIR, 'cloud_flashcard_wrong_state.png') });
  console.log('Saved cloud_flashcard_wrong_state.png');

  const flashRevealBtn = await pageC.$('#reveal-btn');
  if (flashRevealBtn) {
    await flashRevealBtn.click();
    await pageC.waitForTimeout(400);
    await pageC.screenshot({ path: path.join(ARTIFACT_DIR, 'cloud_flashcard_revealed_state.png') });
    console.log('Saved cloud_flashcard_revealed_state.png');
  }

  await browser.close();
  console.log('ALL SCREENSHOTS CAPTURED SUCCESSFULLY!');
}

run().catch(console.error);
