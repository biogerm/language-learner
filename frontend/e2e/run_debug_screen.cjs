const { chromium } = require('playwright');
const path = require('path');

const ARTIFACT_DIR = process.env.ARTIFACT_DIR || './screenshots';
const SCREENSHOT_DIR = ARTIFACT_DIR;

async function testPage(url, name) {
  console.log(`[TEST] Launching browser for ${name}...`);
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  console.log(`[TEST] Going to ${url}...`);
  await page.goto(url, { timeout: 10000 });
  console.log(`[TEST] Loaded ${url}, title: ${await page.title()}`);
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(ARTIFACT_DIR, `${name}.png`) });
  console.log(`[TEST] Screenshot saved to ${name}.png`);
  await browser.close();
}

(async () => {
  try {
    await testPage('http://127.0.0.1:8000/dictation.html', 'compare_legacy_dictation');
    await testPage('http://127.0.0.1:8000/flashcard.html', 'compare_legacy_flashcard');
    await testPage('http://127.0.0.1:5173/login', 'compare_cloud_login');
  } catch(e) {
    console.error('[ERROR]', e);
  }
})();
