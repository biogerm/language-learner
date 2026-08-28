const { chromium } = require('playwright');
const path = require('path');

const ARTIFACT_DIR = './reports/a5d1ee7a-3f21-4b48-8371-19932f1e650d';

async function run() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1000, height: 850 } });

  await page.goto('http://localhost:5173/login');
  await page.fill('input[type="email"]', 'test@example.com');
  await page.fill('input[type="password"]', 'test_password_placeholder');
  await page.click('button[type="submit"]');
  await page.waitForTimeout(1500);

  // Seed into Dexie
  await page.evaluate(async () => {
    // import dexie db from window or execute dexie put
    const req = indexedDB.open('LanguageLearnerDB');
    req.onsuccess = (e) => {
      const db = e.target.result;
      const tx = db.transaction('fsrs_progress', 'readwrite');
      const store = tx.objectStore('fsrs_progress');
      store.put({
        word_id: 'relationer',
        course_id: 'sfid',
        state: 1,
        due: new Date(Date.now() - 100000),
        stability: 1.2,
        difficulty: 4.5,
        elapsed_days: 0,
        scheduled_days: 1,
        reps: 1,
        lapses: 0,
        todayDictationPassed: false,
        todayFlashcardPassed: false
      });
    };
  });
  await page.waitForTimeout(500);

  // Active Dictation Review
  await page.goto('http://localhost:5173/dictation/sfid');
  await page.waitForTimeout(1000);
  const revBtn = await page.$('#fsrs-mode-toggle button:has-text("Review")');
  if (revBtn) await revBtn.click();
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'dictation_active_card_review.png') });

  // Active Flashcard Review
  await page.goto('http://localhost:5173/flashcard/sfid');
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'flashcard_active_card_review.png') });

  // Reveal Flashcard in Review
  const fRevBtn = await page.$('#reveal-btn');
  if (fRevBtn) await fRevBtn.click();
  await page.waitForTimeout(500);
  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'flashcard_active_card_revealed_ratings.png') });

  console.log('Active card review captured successfully!');
  await browser.close();
}

run().catch(console.error);
