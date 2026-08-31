const { chromium } = require('playwright');
const path = require('path');

const ARTIFACT_DIR = process.env.ARTIFACT_DIR || './screenshots';
const SCREENSHOT_DIR = ARTIFACT_DIR;

async function run() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1000, height: 800 } });
  
  // 1. Legacy Dictation
  try {
    const pageL1 = await context.newPage();
    await pageL1.goto('http://127.0.0.1:8000/dictation.html', { waitUntil: 'networkidle', timeout: 5000 }).catch(() => {});
    await pageL1.evaluate(() => {
      localStorage.setItem('sharedCourse', 'sfid');
      localStorage.setItem('appMode', 'study');
    });
    await pageL1.goto('http://127.0.0.1:8000/dictation.html', { waitUntil: 'networkidle', timeout: 5000 }).catch(() => {});
    await pageL1.waitForTimeout(500);
    await pageL1.selectOption('#stage-select', 'stage_01').catch(() => {});
    await pageL1.waitForTimeout(300);
    await pageL1.selectOption('#article-select', 'art_00').catch(() => {});
    await pageL1.waitForTimeout(500);
    await pageL1.screenshot({ path: path.join(ARTIFACT_DIR, 'compare_legacy_dictation.png') });
    console.log('1. compare_legacy_dictation.png saved');
    await pageL1.close();
  } catch(e) { console.error('L1 err:', e); }

  // 2. Legacy Flashcard
  try {
    const pageL2 = await context.newPage();
    await pageL2.goto('http://127.0.0.1:8000/flashcard.html', { waitUntil: 'networkidle', timeout: 5000 }).catch(() => {});
    await pageL2.evaluate(() => {
      localStorage.setItem('sharedCourse', 'sfid');
      localStorage.setItem('appMode', 'study');
    });
    await pageL2.goto('http://127.0.0.1:8000/flashcard.html', { waitUntil: 'networkidle', timeout: 5000 }).catch(() => {});
    await pageL2.waitForTimeout(500);
    await pageL2.selectOption('#stage-select', 'stage_01').catch(() => {});
    await pageL2.waitForTimeout(300);
    await pageL2.selectOption('#article-select', 'art_00').catch(() => {});
    await pageL2.waitForTimeout(500);
    await pageL2.screenshot({ path: path.join(ARTIFACT_DIR, 'compare_legacy_flashcard.png') });
    console.log('2. compare_legacy_flashcard.png saved');
    await pageL2.close();
  } catch(e) { console.error('L2 err:', e); }

  // 3. Cloud Login & Dictation
  try {
    const pageC1 = await context.newPage();
    await pageC1.goto('http://127.0.0.1:5173/login', { waitUntil: 'networkidle', timeout: 5000 }).catch(() => {});
    await pageC1.fill('input[type="email"]', 'test@example.com');
    await pageC1.fill('input[type="password"]', process.env.TEST_USER_PASSWORD || 'test-password');
    await pageC1.click('button[type="submit"]');
    await pageC1.waitForTimeout(1500);

    await pageC1.goto('http://127.0.0.1:5173/dictation/sfid', { waitUntil: 'networkidle', timeout: 5000 }).catch(() => {});
    await pageC1.waitForTimeout(1000);
    await pageC1.selectOption('#stage-select', 'stage_01').catch(() => {});
    await pageC1.waitForTimeout(300);
    await pageC1.selectOption('#article-select', 'art_00').catch(() => {});
    await pageC1.waitForTimeout(500);
    await pageC1.screenshot({ path: path.join(ARTIFACT_DIR, 'compare_cloud_dictation.png') });
    console.log('3. compare_cloud_dictation.png saved');
    await pageC1.close();
  } catch(e) { console.error('C1 err:', e); }

  // 4. Cloud Flashcard
  try {
    const pageC2 = await context.newPage();
    await pageC2.goto('http://127.0.0.1:5173/flashcard/sfid', { waitUntil: 'networkidle', timeout: 5000 }).catch(() => {});
    await pageC2.waitForTimeout(1000);
    await pageC2.selectOption('#stage-select', 'stage_01').catch(() => {});
    await pageC2.waitForTimeout(300);
    await pageC2.selectOption('#article-select', 'art_00').catch(() => {});
    await pageC2.waitForTimeout(500);
    await pageC2.screenshot({ path: path.join(ARTIFACT_DIR, 'compare_cloud_flashcard.png') });
    console.log('4. compare_cloud_flashcard.png saved');
    await pageC2.close();
  } catch(e) { console.error('C2 err:', e); }

  await browser.close();
  console.log('ALL DONE!');
}

run();
