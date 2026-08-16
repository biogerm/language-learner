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
    await page.type('input[type="email"]', 'test@example.com');
    await page.type('input[type="password"]', 'test_password_placeholder');
    await page.click('button[type="submit"]');
    
    // Wait for either navigation to dashboard or an error message to appear
    await page.waitForNavigation({ waitUntil: 'networkidle0', timeout: 5000 }).catch(() => {});
    
    console.log('Page loaded after login. Current URL:', page.url());
    const content = await page.content();
    console.log('Body length:', content.length);
    if (content.length < 1000) console.log(content);
  } catch (error) {
    console.error('Test failed:', error);
  } finally {
    await browser.close();
  }
})();
