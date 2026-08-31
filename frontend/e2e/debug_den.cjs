const { chromium } = require('playwright');
const path = require('path');

async function debugDen() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  
  // Login
  await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
  await page.fill('input[type="email"]', process.env.TEST_USER_EMAIL || 'test@example.com');
  await page.fill('input[type="password"]', process.env.TEST_USER_PASSWORD || 'test-password');
  await page.click('button[type="submit"]');
  await page.waitForTimeout(1500);
  
  // Clear localStorage
  await page.evaluate(() => {
    localStorage.removeItem('customVocab');
    localStorage.removeItem('excludedVocab');
  });
  
  // Clear IndexedDB course_data
  await page.evaluate(() => {
    return new Promise((resolve, reject) => {
      const openReq = indexedDB.open('LanguageLearnerDB');
      openReq.onerror = () => resolve(null);
      openReq.onsuccess = () => {
        const db = openReq.result;
        const storesToClear = Array.from(db.objectStoreNames).filter(s =>
          ['course_data', 'learning_queue', 'custom_dictionary'].includes(s)
        );
        if (storesToClear.length === 0) { resolve(null); return; }
        const tx = db.transaction(storesToClear, 'readwrite');
        tx.oncomplete = () => resolve(null);
        tx.onerror = () => reject(tx.error);
        for (const s of storesToClear) {
          tx.objectStore(s).clear();
        }
      };
    });
  });
  
  // Navigate to Narration
  await page.goto('http://localhost:5173/narration/sfid', { waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);
  await page.locator('select').first().selectOption('stage_12');
  await page.waitForTimeout(1000);
  await page.locator('select').nth(1).selectOption('art_58');
  await page.waitForTimeout(2000);
  
  // Enter edit mode
  const s1 = page.locator('.sentence-card').first();
  await s1.hover();
  await s1.locator('.extract-vocab-btn').click();
  await page.waitForTimeout(1500); // past karaoke
  
  // Check all selectable words
  const wordData = await page.evaluate(() => {
    const words = document.querySelectorAll('.selectable-word');
    const data = [];
    for (const w of words) {
      data.push({
        text: w.textContent,
        class: w.className,
        type: w.getAttribute('data-type')
      });
    }
    return data;
  });
  
  console.log('All selectable words:', JSON.stringify(wordData, null, 2));
  
  // Check localStorage customVocab
  const customVocab = await page.evaluate(() => localStorage.getItem('customVocab'));
  console.log('customVocab in localStorage:', customVocab);
  
  // Click den
  const denEl = page.locator('.selectable-word[data-word="den"]');
  if (await denEl.count() > 0) {
    console.log('Found den element, clicking...');
    await denEl.click();
    await page.waitForTimeout(300);
    const denClass = await denEl.getAttribute('class');
    console.log('den class after click:', denClass);
  } else {
    console.log('den element not found by data-word attribute');
    // Try by text
    const allWords = await page.locator('.selectable-word').allTextContents();
    console.log('All selectable word texts:', allWords);
  }
  
  await browser.close();
}
debugDen().catch(e => { console.error(e); process.exit(1); });
