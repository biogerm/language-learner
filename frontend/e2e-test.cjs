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
    console.log('Navigating to http://localhost:5173/login');
    await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle0' });
    console.log('Login page loaded.');
    await page.waitForSelector('input[type="email"]', { timeout: 2000 });
    await page.type('input[type="email"]', 'test@example.com');
    await page.type('input[type="password"]', 'test_password_placeholder');
    await page.click('button[type="submit"]');
    await page.waitForNavigation({ waitUntil: 'networkidle0' });
    console.log('Navigated after login.');
  } catch (error) {
    console.error('Test failed:', error);
    process.exit(1);
  } finally {
    await browser.close();
  }
})();
