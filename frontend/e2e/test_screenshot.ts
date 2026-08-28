import { chromium } from '@playwright/test';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  page.on('console', msg => console.log('5173 CONSOLE:', msg.text()));
  page.on('pageerror', err => console.log('5173 ERROR:', err.message));

  console.log('Navigating to 5173...');
  await page.goto('http://localhost:5173/');
  await page.waitForTimeout(2000);
  await page.screenshot({ path: 'test-results/5173.png' });
  console.log('Saved 5173.png');
  
  const page2 = await browser.newPage();
  page2.on('console', msg => console.log('5174 CONSOLE:', msg.text()));
  page2.on('pageerror', err => console.log('5174 ERROR:', err.message));

  console.log('Navigating to 5174...');
  await page2.goto('http://localhost:5174/');
  await page2.waitForTimeout(2000);
  await page2.screenshot({ path: 'test-results/5174.png' });
  console.log('Saved 5174.png');

  await browser.close();
})();
