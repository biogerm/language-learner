const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });
  
  await page.goto('http://localhost:5173/dictation/sfid');
  await new Promise(r => setTimeout(r, 2000));
  
  const emailInput = await page.$('input[type="email"]');
  if (emailInput) {
    await page.type('input[type="email"]', process.env.TEST_USER_EMAIL || 'test@example.com');
    await page.type('input[type="password"]', process.env.TEST_USER_PASSWORD || 'test-password');
    await page.click('button[type="submit"]');
    await new Promise(r => setTimeout(r, 2000));
    await page.goto('http://localhost:5173/dictation/sfid');
    await new Promise(r => setTimeout(r, 1000));
  }
  
  await page.evaluate(() => {
    const stageSelect = document.getElementById('stage-select');
    stageSelect.value = 'stage_12';
    stageSelect.dispatchEvent(new Event('change', { bubbles: true }));
  });
  await new Promise(r => setTimeout(r, 500));
  await page.evaluate(() => {
    const articleSelect = document.getElementById('article-select');
    articleSelect.value = 'art_58';
    articleSelect.dispatchEvent(new Event('change', { bubbles: true }));
  });
  
  await new Promise(r => setTimeout(r, 3000));
  
  const count = await page.evaluate(() => {
    const el = document.getElementById('stat-total');
    return el ? el.innerText : 'Not found';
  });
  console.log("Word count WITHOUT clearing DB:", count);
  
  await browser.close();
})();
