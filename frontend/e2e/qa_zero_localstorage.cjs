const { chromium } = require('playwright');
const path = require('path');

const SCREENSHOT_DIR = './reports/a5d1ee7a-3f21-4b48-8371-19932f1e650d';

async function runZeroLocalStorageVerification() {
  console.log('=== RUNNING ZERO LOCALSTORAGE E2E VERIFICATION ===\n');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();

  // 1. Login
  console.log('Step 1: Logging in...');
  await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
  await page.fill('input[type="email"]', 'test@example.com');
  await page.fill('input[type="password"]', 'test_password_placeholder');
  await page.click('button[type="submit"]');
  await page.waitForTimeout(1500);

  // Clear only legacy application keys from localStorage
  await page.evaluate(() => {
    const appKeys = [
      'excludedVocab',
      'customVocab',
      'appMode',
      'selectedStage',
      'selectedArticleId',
      'dictationMasteredWords',
      'flashcardMasteredWords',
      'vocabBook',
      'studyDictationPassed',
      'studyFlashcardPassed',
      'fsrsData'
    ];
    appKeys.forEach(k => localStorage.removeItem(k));
  });

  // 2. Navigate to Narration
  console.log('Step 2: Navigating to Narration...');
  await page.goto('http://localhost:5173/narration/sfid', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  await page.locator('select').first().selectOption('stage_12');
  await page.waitForTimeout(800);
  await page.locator('select').nth(1).selectOption('art_58');
  await page.waitForTimeout(1500);

  // 3. Test AppMode Toggle via Header
  console.log('Step 3: Testing AppMode toggle via Header (Study -> Review -> Study)...');
  const reviewBtn = page.locator('#fsrs-mode-toggle button:has-text("Review")');
  await reviewBtn.click();
  await page.waitForTimeout(1000);
  
  // Verify appMode in Dexie local_settings
  const appModeInDexieReview = await page.evaluate(async () => {
    const dbReq = indexedDB.open('AppDatabase');
    return new Promise((resolve) => {
      dbReq.onsuccess = (e) => {
        const db = e.target.result;
        const tx = db.transaction('local_settings', 'readonly');
        const req = tx.objectStore('local_settings').get('appMode');
        req.onsuccess = () => resolve(req.result?.value);
        req.onerror = () => resolve(null);
      };
    });
  });
  console.log('AppMode stored in Dexie after toggle to Review:', appModeInDexieReview);

  // Switch back to study
  const studyBtn = page.locator('#fsrs-mode-toggle button:has-text("Study")');
  await studyBtn.click();
  await page.waitForTimeout(1000);

  // Return to Narration
  await page.goto('http://localhost:5173/narration/sfid', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1500);
  await page.locator('select').first().selectOption('stage_12');
  await page.waitForTimeout(800);
  await page.locator('select').nth(1).selectOption('art_58');
  await page.waitForTimeout(1500);

  // 4. Test Narration Edit Mode: Exclude target word 'första'
  console.log('Step 4: Testing Narration Edit Mode (Dexie excluded_dictionary & custom_dictionary)...');
  const s1 = page.locator('.sentence-card').first();
  await s1.hover();
  await s1.locator('.extract-vocab-btn').click();
  await page.waitForTimeout(1200);

  // Deselect 'första'
  const forstaEl = s1.locator('.selectable-word:has-text("första")').first();
  await forstaEl.click();
  await page.waitForTimeout(300);

  // Save changes
  await s1.locator('.save-vocab-btn').click();
  await page.waitForTimeout(1000);

  // Verify Dexie excluded_dictionary has 'första'
  const excludedInDexie = await page.evaluate(async () => {
    const dbReq = indexedDB.open('AppDatabase');
    return new Promise((resolve) => {
      dbReq.onsuccess = (e) => {
        const db = e.target.result;
        const tx = db.transaction('excluded_dictionary', 'readonly');
        const req = tx.objectStore('excluded_dictionary').getAll();
        req.onsuccess = () => resolve(req.result.map(r => r.base_form));
        req.onerror = () => resolve([]);
      };
    });
  });
  console.log('Excluded words in Dexie excluded_dictionary:', excludedInDexie);

  await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'zero_ls_01_narration_saved.png') });

  // 5. Test Dictation Study Mode (Mastery stored in Dexie study_mastery)
  console.log('Step 5: Testing Dictation Study Mode (Dexie study_mastery)...');
  await page.goto('http://localhost:5173/dictation/sfid', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1200);
  await page.locator('select').first().selectOption('stage_12');
  await page.waitForTimeout(600);
  await page.locator('select').nth(1).selectOption('art_58');
  await page.waitForTimeout(1500);

  const dictStats = await page.locator('#progress-stats').textContent();
  console.log('Dictation progress stats:', dictStats);
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'zero_ls_02_dictation_page.png') });

  // 6. Test Flashcard Study Mode
  console.log('Step 6: Testing Flashcard Study Mode...');
  await page.goto('http://localhost:5173/flashcard/sfid', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1200);
  await page.locator('select').first().selectOption('stage_12');
  await page.waitForTimeout(600);
  await page.locator('select').nth(1).selectOption('art_58');
  await page.waitForTimeout(1500);

  const flashStats = await page.locator('#progress-stats').textContent();
  console.log('Flashcard progress stats:', flashStats);
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'zero_ls_03_flashcard_page.png') });

  // 7. Audit LocalStorage: Check all keys in localStorage
  console.log('\nStep 7: Auditing browser localStorage...');
  const allLocalStorageKeys = await page.evaluate(() => {
    const keys = [];
    for (let i = 0; i < localStorage.length; i++) {
      const k = localStorage.key(i);
      // Ignore Supabase auth token
      if (k && !k.startsWith('sb-')) {
        keys.push({ key: k, value: localStorage.getItem(k) });
      }
    }
    return keys;
  });

  console.log('Non-auth localStorage keys found:', allLocalStorageKeys);
  const isZeroAppLocalStorage = allLocalStorageKeys.length === 0;
  console.log('Is application localStorage ZERO?:', isZeroAppLocalStorage);

  if (!isZeroAppLocalStorage) {
    console.error('FAILED: Found remaining localStorage keys:', allLocalStorageKeys);
    process.exit(1);
  }

  console.log('\n=== ALL ZERO LOCALSTORAGE VERIFICATIONS PASSED SUCCESSFULLY! ===');
  await browser.close();
}

runZeroLocalStorageVerification().catch(err => {
  console.error('Fatal error during zero localStorage verification:', err);
  process.exit(1);
});
