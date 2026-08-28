const { chromium } = require('playwright');

async function run() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  await page.goto('http://localhost:5173/login');
  await page.fill('input[type="email"]', 'test@example.com');
  await page.fill('input[type="password"]', 'test_password_placeholder');
  await page.click('button[type="submit"]');
  await page.waitForTimeout(1500);

  // Navigate to dictation to let DataContext load courseData and sync Supabase
  await page.goto('http://localhost:5173/dictation/sfid');
  await page.waitForTimeout(2000);

  const result = await page.evaluate(async () => {
    // 1. Get all words in fsrs_progress
    const db = await new Promise((resolve, reject) => {
      const req = indexedDB.open('AppDatabase');
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });

    const fsrsWords = await new Promise((resolve) => {
      const tx = db.transaction('fsrs_progress', 'readonly');
      const store = tx.objectStore('fsrs_progress');
      const req = store.getAll();
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => resolve([]);
    });

    // 2. Get courseData from course_data store
    const courseDataRecord = await new Promise((resolve) => {
      const tx = db.transaction('course_data', 'readonly');
      const store = tx.objectStore('course_data');
      const req = store.get('sfid');
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => resolve(null);
    });

    return {
      fsrsRecords: fsrsWords,
      courseData: courseDataRecord
    };
  });

  console.log('FSRS Records count:', result.fsrsRecords.length);
  console.log('FSRS Records:', JSON.stringify(result.fsrsRecords, null, 2));

  await browser.close();
}

run().catch(console.error);
