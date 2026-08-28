const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });
  await page.goto('http://localhost:5173/dictation/sfid');
  await new Promise(r => setTimeout(r, 2000));
  const text = await page.evaluate(() => document.body.innerText);
  console.log(text);
  await browser.close();
})();
