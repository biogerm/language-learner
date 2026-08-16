const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();
  
  await page.goto('http://localhost:5174/login');
  await page.waitForSelector('input[type="email"]');
  await page.type('input[type="email"]', 'test@example.com');
  await page.type('input[type="password"]', 'test_password_placeholder');
  await page.click('button[type="submit"]');
  
  await page.waitForNavigation();
  await page.goto('http://localhost:5174/narration/sfid');
  
  await new Promise(r => setTimeout(r, 2000));
  
  const sentences = await page.$$eval('.sentence-sv', els => els.length);
  console.log('Swedish sentences found:', sentences);
  
  const options = await page.$$eval('select option', els => els.map(e => e.textContent));
  console.log('Select options:', options);
  
  await browser.close();
})();
