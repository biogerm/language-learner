const { chromium } = require('playwright');

async function run() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  await page.goto('http://localhost:5173/login');
  await page.fill('input[type="email"]', 'test@example.com');
  await page.fill('input[type="password"]', 'test_password_placeholder');
  await page.click('button[type="submit"]');
  await page.waitForTimeout(1500);

  const res = await page.evaluate(async () => {
    const db = await new Promise((resolve, reject) => {
      const req = indexedDB.open('AppDatabase');
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });

    async function getStore(name) {
      const tx = db.transaction(name, 'readonly');
      const store = tx.objectStore(name);
      return new Promise((resolve) => {
        const req = store.getAll();
        req.onsuccess = () => resolve(req.result);
        req.onerror = () => resolve([]);
      });
    }

    const lq = await getStore('learning_queue');
    const cd = await getStore('custom_dictionary');
    const fsrs = await getStore('fsrs_progress');
    const ls = { ...localStorage };

    return {
      learning_queue_count: lq.length,
      learning_queue: lq,
      custom_dictionary_count: cd.length,
      custom_dictionary: cd,
      fsrs_count: fsrs.length,
      localStorage: ls
    };
  });

  console.log('Stores state:', JSON.stringify(res, null, 2));
  await browser.close();
}

run().catch(console.error);
