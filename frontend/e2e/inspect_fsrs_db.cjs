const { chromium } = require('playwright');

async function run() {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  await page.goto('http://localhost:5173/login');
  await page.fill('input[type="email"]', 'test@example.com');
  await page.fill('input[type="password"]', 'test_password_placeholder');
  await page.click('button[type="submit"]');
  await page.waitForTimeout(1500);

  const data = await page.evaluate(async () => {
    return new Promise((resolve) => {
      const req = indexedDB.open('LanguageLearnerDB');
      req.onsuccess = (e) => {
        const db = e.target.result;
        const tx = db.transaction(['fsrs_progress'], 'readonly');
        const store = tx.objectStore('fsrs_progress');
        const getReq = store.getAll();
        getReq.onsuccess = () => resolve(getReq.result);
        getReq.onerror = () => resolve([]);
      };
      req.onerror = () => resolve([]);
    });
  });

  console.log('Total fsrs_progress count:', data.length);
  console.log('FSRS words in DB:', JSON.stringify(data.map(d => ({ word_id: d.word_id, state: d.state, due: d.due, todayDictationPassed: d.todayDictationPassed, todayFlashcardPassed: d.todayFlashcardPassed })), null, 2));

  await browser.close();
}

run().catch(console.error);
