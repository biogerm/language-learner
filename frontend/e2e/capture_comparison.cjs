const { chromium } = require('playwright');
const path = require('path');

const ARTIFACT_DIR = process.env.ARTIFACT_DIR || './screenshots';
const SCREENSHOT_DIR = ARTIFACT_DIR;

async function run() {
  console.log('Starting browser...');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1000, height: 800 } });
  
  // Page 1: Legacy App
  const pageL = await context.newPage();
  console.log('Navigating to legacy dictation...');
  await pageL.goto('http://127.0.0.1:8000/dictation.html');
  await pageL.evaluate(() => {
    localStorage.setItem('sharedCourse', 'sfid');
    localStorage.setItem('appMode', 'study');
  });
  await pageL.goto('http://127.0.0.1:8000/dictation.html');
  await pageL.waitForTimeout(500);
  await pageL.selectOption('#stage-select', 'stage_01').catch(e => console.log('stage select err:', e.message));
  await pageL.waitForTimeout(200);
  await pageL.selectOption('#article-select', 'art_00').catch(e => console.log('art select err:', e.message));
  await pageL.waitForTimeout(500);
  await pageL.screenshot({ path: path.join(ARTIFACT_DIR, 'compare_legacy_dictation.png') });
  console.log('Legacy dictation captured');

  console.log('Navigating to legacy flashcard...');
  await pageL.goto('http://127.0.0.1:8000/flashcard.html');
  await pageL.evaluate(() => {
    localStorage.setItem('sharedCourse', 'sfid');
    localStorage.setItem('appMode', 'study');
  });
  await pageL.goto('http://127.0.0.1:8000/flashcard.html');
  await pageL.waitForTimeout(500);
  await pageL.selectOption('#stage-select', 'stage_01').catch(e => console.log('stage select err:', e.message));
  await pageL.waitForTimeout(200);
  await pageL.selectOption('#article-select', 'art_00').catch(e => console.log('art select err:', e.message));
  await pageL.waitForTimeout(500);
  await pageL.screenshot({ path: path.join(ARTIFACT_DIR, 'compare_legacy_flashcard.png') });
  console.log('Legacy flashcard captured');

  // Page 2: Cloud App
  const pageC = await context.newPage();
  console.log('Navigating to cloud login...');
  await pageC.goto('http://127.0.0.1:5173/login');
  await pageC.waitForSelector('input[type="email"]', { timeout: 5000 });
  await pageC.fill('input[type="email"]', 'test@example.com');
  await pageC.fill('input[type="password"]', process.env.TEST_USER_PASSWORD || 'test-password');
  await pageC.click('button[type="submit"]');
  await pageC.waitForTimeout(1500);

  console.log('Navigating to cloud dictation...');
  await pageC.goto('http://127.0.0.1:5173/dictation/sfid');
  await pageC.waitForTimeout(1500);
  await pageC.selectOption('#stage-select', 'stage_01').catch(e => console.log('cloud stage err:', e.message));
  await pageC.waitForTimeout(200);
  await pageC.selectOption('#article-select', 'art_00').catch(e => console.log('cloud art err:', e.message));
  await pageC.waitForTimeout(500);
  await pageC.screenshot({ path: path.join(ARTIFACT_DIR, 'compare_cloud_dictation.png') });
  console.log('Cloud dictation captured');

  console.log('Navigating to cloud flashcard...');
  await pageC.goto('http://127.0.0.1:5173/flashcard/sfid');
  await pageC.waitForTimeout(1500);
  await pageC.selectOption('#stage-select', 'stage_01').catch(e => console.log('cloud stage err:', e.message));
  await pageC.waitForTimeout(200);
  await pageC.selectOption('#article-select', 'art_00').catch(e => console.log('cloud art err:', e.message));
  await pageC.waitForTimeout(500);
  await pageC.screenshot({ path: path.join(ARTIFACT_DIR, 'compare_cloud_flashcard.png') });
  console.log('Cloud flashcard captured');

  await browser.close();
  console.log('ALL DONE SUCCESS!');
}

run().catch(console.error);
