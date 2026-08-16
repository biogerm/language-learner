const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.goto('http://localhost:5173/login');
  await page.type('input[type="email"]', 'user1@example.com');
  await page.type('input[type="password"]', 'password');
  await page.click('button[type="submit"]');
  await new Promise(r => setTimeout(r, 2000));
  const error = await page.$eval('.error-message', el => el.innerText).catch(() => 'No error message');
  console.log('Login error:', error);
  await browser.close();
})();
