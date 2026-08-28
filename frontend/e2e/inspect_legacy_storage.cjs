const { chromium } = require('playwright');

async function run() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  await page.goto('http://127.0.0.1:8000/dictation.html');
  const ls = await page.evaluate(() => {
    return { ...localStorage };
  });

  console.log('Legacy app localStorage:', JSON.stringify(ls, null, 2));

  // Also check if any stage has 13 words
  const stageStats = await page.evaluate(() => {
    if (typeof DICTATION_WORDS === 'undefined') return 'DICTATION_WORDS undefined';
    const counts = {};
    DICTATION_WORDS.forEach(w => {
      const k = `${w.stage} / ${w.article}`;
      counts[k] = (counts[k] || 0) + 1;
    });
    return Object.entries(counts).filter(([k, v]) => v === 13);
  });
  console.log('Stages/Articles with exactly 13 words:', stageStats);

  await browser.close();
}

run().catch(console.error);
