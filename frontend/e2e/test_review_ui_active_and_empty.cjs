const { chromium } = require('playwright');
const path = require('path');

const ARTIFACT_DIR = './reports/a5d1ee7a-3f21-4b48-8371-19932f1e650d';

async function run() {
  console.log('Testing unified test UI in Review mode...');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1000, height: 850 } });
  const page = await context.newPage();

  // Login
  await page.goto('http://localhost:5173/login');
  await page.fill('input[type="email"]', 'test@example.com');
  await page.fill('input[type="password"]', 'test_password_placeholder');
  await page.click('button[type="submit"]');
  await page.waitForTimeout(1500);

  // 1. Review Mode (Empty queue state)
  await page.goto('http://localhost:5173/dictation/sfid');
  await page.waitForTimeout(1000);
  const reviewToggleD = await page.$('#fsrs-mode-toggle button:has-text("Review")');
  if (reviewToggleD) await reviewToggleD.click();
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'dictation_review_empty_unified.png') });

  await page.goto('http://localhost:5173/flashcard/sfid');
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'flashcard_review_empty_unified.png') });

  // 2. Seed 2 due words into Dexie FSRS progress for active review test
  console.log('Seeding 2 test cards into FSRS...');
  await page.evaluate(async () => {
    // Access dexie via window or indexedDB
    const req = indexedDB.open('LanguageLearnerDB');
    req.onsuccess = (e) => {
      const db = e.target.result;
      const tx = db.transaction('fsrs_progress', 'readwrite');
      const store = tx.objectStore('fsrs_progress');
      const pastDue = new Date(Date.now() - 3600000);
      store.put({
        word_id: 'komma',
        course_id: 'sfid',
        state: 1,
        due: pastDue,
        stability: 1,
        difficulty: 5,
        elapsed_days: 0,
        scheduled_days: 1,
        reps: 1,
        lapses: 0,
        todayDictationPassed: false,
        todayFlashcardPassed: false
      });
      store.put({
        word_id: 'prata',
        course_id: 'sfid',
        state: 1,
        due: pastDue,
        stability: 1,
        difficulty: 5,
        elapsed_days: 0,
        scheduled_days: 1,
        reps: 1,
        lapses: 0,
        todayDictationPassed: false,
        todayFlashcardPassed: false
      });
    };
  });
  await page.waitForTimeout(1000);

  // 3. Dictation - Active Review Mode
  await page.goto('http://localhost:5173/dictation/sfid');
  await page.waitForTimeout(1500);
  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'dictation_review_active_testing.png') });

  // 4. Flashcard - Active Review Mode
  await page.goto('http://localhost:5173/flashcard/sfid');
  await page.waitForTimeout(1500);
  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'flashcard_review_active_testing.png') });

  // Reveal Flashcard in Review Mode to verify rating buttons
  const revBtn = await page.$('#reveal-btn');
  if (revBtn) await revBtn.click();
  await page.waitForTimeout(500);
  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'flashcard_review_active_ratings.png') });

  console.log('ALL ACTIVE & EMPTY REVIEW TESTING CAPTURED!');
  await browser.close();
}

run().catch(console.error);
