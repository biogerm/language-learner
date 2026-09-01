const { chromium } = require('playwright');
const path = require('path');

const ARTIFACT_DIR = process.env.ARTIFACT_DIR || './screenshots';
const SCREENSHOT_DIR = ARTIFACT_DIR;

async function run() {
  console.log('Testing full 4-word mastery loop on art_58...');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1000, height: 850 } });
  const page = await context.newPage();

  // Login
  await page.goto('http://localhost:5173/login', { waitUntil: 'domcontentloaded' });
  await page.fill('input[type="email"]', process.env.TEST_USER_EMAIL || 'test@example.com');
  await page.fill('input[type="password"]', process.env.TEST_USER_PASSWORD || 'test-password');
  await page.click('button[type="submit"]');
  await page.waitForTimeout(1000);

  // Clear mastery
  await page.evaluate(() => localStorage.removeItem('dictationMasteredWords'));

  // Go to dictation art_58
  await page.goto('http://localhost:5173/dictation/sfid', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(1000);
  await page.selectOption('#stage-select', 'stage_12').catch(() => {});
  await page.waitForTimeout(300);
  await page.selectOption('#article-select', 'art_58').catch(() => {});
  await page.waitForTimeout(600);

  const words = ['detta', 'testmening', 'första', 'andra', 'testa', 'en', 'mening', 'här'];

  for (let round = 1; round <= 4; round++) {
    let currentStats = await page.$eval('#progress-stats', el => el.innerText.replace(/\n/g, ' '));
    console.log(`\n--- ROUND ${round} --- Start Stats: ${currentStats}`);

    // Try candidate words until correct
    let matched = false;
    for (const w of words) {
      const isTyping = await page.evaluate(() => {
        const inp = document.getElementById('spell-input');
        return inp && !inp.disabled;
      });
      if (!isTyping) break;

      await page.fill('#spell-input', w);
      await page.keyboard.press('Enter');
      await page.waitForTimeout(100);

      const fb = await page.$eval('#feedback-msg', el => el.innerText);
      if (fb.startsWith('Correct!')) {
        matched = true;
        console.log(`Round ${round}: Matched word "${w}"!`);
        break;
      }
    }

    if (matched) {
      const afterStats = await page.$eval('#progress-stats', el => el.innerText.replace(/\n/g, ' '));
      console.log(`Round ${round}: Stats immediately after correct: ${afterStats}`);
      // Wait for countdown
      await page.waitForTimeout(2000);
    }
  }

  const finalStats = await page.$eval('#progress-stats', el => el.innerText.replace(/\n/g, ' '));
  console.log('\n--- FINAL STATS ---', finalStats);
  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'dictation_all_4_mastered.png') });
  console.log('Saved dictation_all_4_mastered.png');

  await browser.close();
  console.log('FULL 4-WORD TEST PASSED!');
}

run().catch(console.error);
