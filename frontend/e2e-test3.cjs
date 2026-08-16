const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  
  page.on('console', msg => {
    console.log('BROWSER LOG:', msg.text());
  });
  
  page.on('pageerror', err => {
    console.error('BROWSER PAGE EXCEPTION:', err.message);
  });
  
  try {
    console.log('Navigating to http://localhost:5173/dashboard');
    await page.goto('http://localhost:5173/dashboard', { waitUntil: 'networkidle0' });
    const content = await page.content();
    console.log('Page body length:', content.length);
    if (content.length < 500) {
      console.log('Small page content:', content);
    }
  } catch (error) {
    console.error('Test failed:', error);
  } finally {
    await browser.close();
  }
})();
