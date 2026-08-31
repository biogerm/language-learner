const { chromium } = require('playwright');

async function run() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  await page.goto('http://localhost:5173/login');
  await page.fill('input[type="email"]', 'test@example.com');
  await page.fill('input[type="password"]', process.env.TEST_USER_PASSWORD || 'test-password');
  await page.click('button[type="submit"]');
  await page.waitForTimeout(1500);

  await page.goto('http://localhost:5173/dictation/sfid');
  await page.waitForTimeout(2000);

  const articleInfo = await page.evaluate(async () => {
    const db = await new Promise((resolve) => {
      const req = indexedDB.open('AppDatabase');
      req.onsuccess = () => resolve(req.result);
    });
    const tx = db.transaction('course_data', 'readonly');
    const store = tx.objectStore('course_data');
    const cd = await new Promise((resolve) => {
      const req = store.get('sfid');
      req.onsuccess = () => resolve(req.result);
    });

    if (!cd || !cd.articles || !cd.articles.stages) return null;

    const stages = cd.articles.stages.map(s => ({
      stage_id: s.stage_id,
      stage_title: s.stage_title,
      articles: s.articles.map(a => {
        const words = new Set();
        (a.sentences || []).forEach(sent => {
          (sent.target_words || []).forEach(tw => words.add(tw.base_form));
        });
        return {
          article_id: a.article_id,
          article_title: a.article_title,
          sentence_count: (a.sentences || []).length,
          target_word_count: words.size,
          target_words: Array.from(words)
        };
      })
    }));

    return stages;
  });

  console.log('Article details:', JSON.stringify(articleInfo, null, 2));
  await browser.close();
}

run().catch(console.error);
