const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  
  try {
    await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle0' });
    await page.type('input[type="email"]', 'test@example.com');
    await page.type('input[type="password"]', 'test_password_placeholder');
    await page.click('button[type="submit"]');
    
    await new Promise(r => setTimeout(r, 2000));
    const errorText = await page.$eval('.error-message', el => el.textContent).catch(() => null);
    if (errorText) {
      console.log('LOGIN ERROR MESSAGE:', errorText);
    } else {
      console.log('No error message found. Current URL:', page.url());
    }
  } finally {
    await browser.close();
  }
})();
