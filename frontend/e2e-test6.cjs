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
    console.log('Current URL:', page.url());
    
    const h2 = await page.$eval('h2', el => el.textContent).catch(() => null);
    console.log('H2:', h2);
    
    const courses = await page.$$eval('.course-card h3', els => els.map(e => e.innerText));
    console.log('Courses:', courses);
  } finally {
    await browser.close();
  }
})();
