const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();
  
  page.on('console', msg => console.log('BROWSER LOG:', msg.text()));
  page.on('pageerror', err => console.log('BROWSER ERROR:', err.toString()));
  
  await page.goto('http://localhost:5173/login');
  await page.waitForSelector('input[type="email"]');
  await page.type('input[type="email"]', 'test@example.com');
  await page.type('input[type="password"]', 'test_password_placeholder');
  await page.click('button[type="submit"]');
  
  await page.waitForNavigation();
  console.log('Logged in!');
  
  await page.goto('http://localhost:5173/narration/sfid');
  console.log('Went to Narration sfid!');
  
  // Wait a bit to see if there's an error
  await new Promise(r => setTimeout(r, 3000));
  
  await browser.close();
})();
