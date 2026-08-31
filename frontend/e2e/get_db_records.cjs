const { chromium } = require('playwright');

async function run() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  await page.goto('http://localhost:5173/login');
  await page.fill('input[type="email"]', 'test@example.com');
  await page.fill('input[type="password"]', process.env.TEST_USER_PASSWORD || 'test-password');
  await page.click('button[type="submit"]');
  await page.waitForTimeout(1500);

  const res = await page.evaluate(async () => {
    const db = await new Promise((resolve) => {
      const req = indexedDB.open('LanguageLearnerDB');
      req.onsuccess = () => resolve(req.result);
    });
    const tx = db.transaction('fsrs_progress', 'readonly');
    const store = tx.objectStore('fsrs_progress');
    const req = store.getAll();
    return new Promise((resolve) => {
      req.onsuccess = () => resolve(req.result);
    });
  });

  console.log('Record count:', res.length);
  console.log('Words in fsrs_progress:', res.map(r => r.word_id));
  await browser.close();
}

run().catch(console.error);
