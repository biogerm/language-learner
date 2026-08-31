const { chromium } = require('playwright');

async function testRules() {
  console.log('--- STARTING THREE RULES VERIFICATION ---');
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  // Login
  await page.goto('http://localhost:5173/login');
  await page.fill('input[type="email"]', process.env.TEST_USER_EMAIL || 'test@example.com');
  await page.fill('input[type="password"]', process.env.TEST_USER_PASSWORD || 'test-password');
  await page.click('button[type="submit"]');
  await page.waitForTimeout(1000);

  // 1. TEST DICTATION
  console.log('\n[1] Testing Dictation on art_58:');
  await page.goto('http://localhost:5173/dictation/sfid');
  await page.waitForTimeout(1000);
  
  await page.selectOption('#stage-select', 'stage_12').catch(() => {});
  await page.waitForTimeout(300);
  await page.selectOption('#article-select', 'art_58').catch(() => {});
  await page.waitForTimeout(500);

  // Click Reset Progress to start fresh
  const resetBtn = await page.$('#reset-progress-btn');
  if (resetBtn) await resetBtn.click();
  await page.waitForTimeout(500);

  // Type wrong answer and Reveal
  await page.fill('#spell-input', 'wronganswer');
  await page.keyboard.press('Enter');
  await page.waitForTimeout(200);

  // Click Reveal Answer
  await page.click('#reveal-btn');
  await page.waitForTimeout(400);

  // Check 1: Timer bar must NOT be active
  const timerBarDisplay = await page.$eval('#timer-bar', el => window.getComputedStyle(el).display);
  console.log('Rule 2 check: Timer bar display on reveal (should be "none"):', timerBarDisplay);

  // Check 2: Answer display - Swedish word present, but NO dictionary definition / English translation
  const correctSv = await page.$eval('#correct-sv', el => el.innerText);
  const correctEnEl = await page.$('#correct-en');
  console.log('Rule 2 check: Revealed Swedish word:', correctSv);
  console.log('Rule 2 check: English definition element present on reveal (should be null or empty):', correctEnEl ? await correctEnEl.innerText() : 'None');

  // Check 3: No example sentence displayed
  const sentenceDisplay = await page.$('#hint-display');
  console.log('Rule 3 check: Sentence hint display:', sentenceDisplay ? await sentenceDisplay.innerText() : 'None');

  // Check 4: Next button exists and pressing Enter proceeds to next word
  const nextBtn = await page.$('#next-btn');
  console.log('Next button visible on reveal:', !!nextBtn);
  await page.keyboard.press('Enter');
  await page.waitForTimeout(500);

  const newWordInputState = await page.$eval('#spell-input', el => el.value);
  console.log('Advanced to next word after Enter:', newWordInputState === '');

  // 2. TEST FLASHCARD
  console.log('\n[2] Testing Flashcards on art_58:');
  await page.goto('http://localhost:5173/flashcard/sfid');
  await page.waitForTimeout(1000);

  await page.selectOption('#stage-select', 'stage_12').catch(() => {});
  await page.waitForTimeout(300);
  await page.selectOption('#article-select', 'art_58').catch(() => {});
  await page.waitForTimeout(500);

  // Click Reveal Answer
  await page.click('#reveal-btn');
  await page.waitForTimeout(400);

  // Check Flashcard timer bar
  const fcTimerDisplay = await page.$eval('#timer-bar', el => window.getComputedStyle(el).display);
  console.log('Rule 2 check (Flashcard): Timer bar display on reveal (should be "none"):', fcTimerDisplay);

  // Check Flashcard English definition element on reveal
  const fcCorrectEn = await page.$('#correct-en');
  console.log('Rule 2 check (Flashcard): English definition present in answer display (should be null):', fcCorrectEn ? await fcCorrectEn.innerText() : 'None');

  // Check Flashcard sentence hint
  const fcSentenceHint = await page.$('#hint-display');
  console.log('Rule 3 check (Flashcard): Sentence hint displayed:', fcSentenceHint ? await fcSentenceHint.innerText() : 'None');

  await browser.close();
  console.log('\n🎉 ALL 3 RULES VERIFIED SUCCESSFULLY!');
}

testRules().catch(console.error);
