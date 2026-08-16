const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  
  page.on('console', msg => {
    if (msg.type() === 'error') console.error('BROWSER ERROR:', msg.text());
    else console.log('BROWSER LOG:', msg.text());
  });
  
  page.on('pageerror', err => {
    console.error('BROWSER PAGE EXCEPTION:', err.message);
  });
  
  try {
    console.log('Navigating to http://localhost:5173/');
    await page.goto('http://localhost:5173/', { waitUntil: 'networkidle0' });
    console.log('Page loaded. Current URL:', page.url());
  } catch (error) {
    console.error('Test failed:', error);
  } finally {
    await browser.close();
  }
})();
