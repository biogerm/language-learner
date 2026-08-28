const { chromium } = require('playwright');
const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');

// Read .env.local for supabase keys
const envPath = path.join(__dirname, '.env.local');
let envContent = '';
try {
  envContent = fs.readFileSync(envPath, 'utf8');
} catch (e) {}

let supabaseUrl = '';
let supabaseKey = '';
envContent.split('\n').forEach(line => {
  if (line.startsWith('VITE_SUPABASE_URL=')) supabaseUrl = line.split('=')[1].trim();
  if (line.startsWith('VITE_SUPABASE_ANON_KEY=')) supabaseKey = line.split('=')[1].trim();
});

console.log('Connecting to Supabase at:', supabaseUrl);

async function run() {
  // 1. Clear Supabase cloud table
  if (supabaseUrl && supabaseKey) {
    const supabase = createClient(supabaseUrl, supabaseKey);
    const { data: authData, error: authErr } = await supabase.auth.signInWithPassword({
      email: 'test@example.com',
      password: 'test_password_placeholder'
    });
    
    if (authData?.user) {
      console.log('Authenticated Supabase user:', authData.user.id);
      const { error: delErr } = await supabase
        .from('fsrs_progress')
        .delete()
        .eq('user_id', authData.user.id);
      
      if (delErr) {
        console.error('Error clearing Supabase fsrs_progress:', delErr);
      } else {
        console.log('✓ Successfully cleared Supabase cloud fsrs_progress records for test user.');
      }
    }
  }

  // 2. Clear Browser IndexedDB & LocalStorage via Playwright
  console.log('Launching browser to clear Dexie & LocalStorage...');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1000, height: 850 } });
  const page = await context.newPage();

  await page.goto('http://localhost:5173/login');
  await page.fill('input[type="email"]', 'test@example.com');
  await page.fill('input[type="password"]', 'test_password_placeholder');
  await page.click('button[type="submit"]');
  await page.waitForTimeout(1500);

  const localClearResult = await page.evaluate(async () => {
    // Clear Dexie fsrs_progress
    const db = await new Promise((resolve) => {
      const req = indexedDB.open('AppDatabase');
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => resolve(null);
    });

    if (db) {
      const tx = db.transaction(['fsrs_progress'], 'readwrite');
      const store = tx.objectStore('fsrs_progress');
      store.clear();
      await new Promise(resolve => tx.oncomplete = resolve);
    }

    // Clear legacy localStorage keys
    localStorage.removeItem('fsrsData');
    localStorage.removeItem('studyDictationPassed');
    localStorage.removeItem('studyFlashcardPassed');
    localStorage.removeItem('dictationMasteredWords');
    localStorage.removeItem('flashcardMasteredWords');
    localStorage.removeItem('vocabBook');

    return { success: true };
  });

  console.log('✓ Local IndexedDB & LocalStorage cleared:', localClearResult);

  // 3. Verify Review Mode in Dictation
  await page.goto('http://localhost:5173/dictation/sfid');
  await page.waitForTimeout(1000);
  const revBtn = await page.$('#fsrs-mode-toggle button:has-text("Review")');
  if (revBtn) await revBtn.click();
  await page.waitForTimeout(1000);

  const ARTIFACT_DIR = './reports/a5d1ee7a-3f21-4b48-8371-19932f1e650d';
  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'dictation_after_fsrs_cleared.png') });

  // 4. Verify Review Mode in Flashcard
  await page.goto('http://localhost:5173/flashcard/sfid');
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'flashcard_after_fsrs_cleared.png') });

  console.log('✓ Verified and captured post-clear screenshots successfully!');
  await browser.close();
}

run().catch(console.error);
