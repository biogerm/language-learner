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
    await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle0' });
    await page.type('input[type="email"]', 'test@example.com');
    await page.type('input[type="password"]', 'test_password_placeholder');
    await page.click('button[type="submit"]');
    
    await new Promise(r => setTimeout(r, 2000));
    
    console.log('Navigating to http://localhost:5173/narration/sfid');
    await page.goto('http://localhost:5173/narration/sfid', { waitUntil: 'networkidle0' });
    
    console.log('Page loaded. Current URL:', page.url());
    const h2 = await page.$eval('h2', el => el.textContent).catch(() => null);
    console.log('H2:', h2);
  } finally {
    await browser.close();
  }
})();
