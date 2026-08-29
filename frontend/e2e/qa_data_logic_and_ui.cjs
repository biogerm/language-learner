const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

async function run() {
  const screenshotsDir = path.join(__dirname, 'screenshots');
  if (!fs.existsSync(screenshotsDir)) {
    fs.mkdirSync(screenshotsDir, { recursive: true });
  }

  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });

  page.on('console', msg => console.log(`[BROWSER CONSOLE ${msg.type()}]:`, msg.text()));
  page.on('pageerror', err => console.log(`[BROWSER ERROR]:`, err.message));

  console.log('🚀 Step 0: Logging in at http://localhost:5173/login...');
  await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle2' });
  await page.type('input[type="email"]', 'test@example.com');
  await page.type('input[type="password"]', 'test_password_placeholder');
  await page.click('button[type="submit"]');
  await new Promise(r => setTimeout(r, 2000));

  console.log('🚀 Step 1: Loading http://localhost:5173/narration/sfid...');
  await page.goto('http://localhost:5173/narration/sfid', { waitUntil: 'networkidle2' });
  await new Promise(r => setTimeout(r, 1500));

  // Step 2: Test Read Mode Highlight Removal & Edit Mode Badge
  console.log('\n🔍 Step 2: Testing Read Mode & Edit Mode with FSRS words...');
  await page.evaluate(async () => {
    const { db } = await import('/src/db/dexie.ts');
    await db.fsrs_progress.clear();
    await db.fsrs_progress.put({
      word_id: 'till',
      course_id: 'sfid',
      state: 1,
      due: new Date(Date.now() - 100000),
      stability: 2,
      difficulty: 5,
      elapsed_days: 0,
      scheduled_days: 1,
      reps: 1,
      lapses: 0,
      last_review: new Date()
    });
  });

  await page.reload({ waitUntil: 'networkidle2' });
  
  // Wait for sentence cards to render with generous timeout
  await page.waitForSelector('.sentence-card', { timeout: 15000 });
  await new Promise(r => setTimeout(r, 1000));

  // Check if 'till' is highlighted as a target word in Read Mode
  const isTillTargetInReadMode = await page.evaluate(() => {
    const targetWords = Array.from(document.querySelectorAll('.vocab-word.target-word'));
    return targetWords.some(el => el.textContent.trim().toLowerCase() === 'till');
  });
  console.log(`- Is 'till' highlighted as target in Read Mode? ${isTillTargetInReadMode} (Expected: false)`);
  if (isTillTargetInReadMode) {
    throw new Error("FAIL: 'till' is active in FSRS but still highlighted as target in Read Mode!");
  }

  // Click edit button on the sentence that contains 'till'
  await page.evaluate(() => {
    const cards = Array.from(document.querySelectorAll('.sentence-card'));
    for (const card of cards) {
      if (card.textContent && card.textContent.toLowerCase().includes('till')) {
        const btn = card.querySelector('.extract-vocab-btn');
        if (btn) {
          btn.click();
          break;
        }
      }
    }
  });
  await new Promise(r => setTimeout(r, 1200));

  // Inspect all tokens in Edit Mode
  const editTokens = await page.evaluate(() => {
    const tokens = Array.from(document.querySelectorAll('.selectable-word'));
    return tokens.map(t => ({
      text: t.textContent.trim(),
      className: t.className,
      inner: t.innerHTML
    }));
  });
  console.log('Edit Mode Tokens:', JSON.stringify(editTokens, null, 2));

  // Check for the ✓ badge in Edit Mode
  const badgeExists = await page.evaluate(() => {
    const badge = document.querySelector('.fsrs-review-badge');
    return badge ? badge.textContent.trim() : null;
  });
  console.log(`- Badge in Edit Mode for 'till': "${badgeExists}" (Expected: "✓")`);
  if (badgeExists !== '✓') {
    throw new Error("FAIL: FSRS checkmark badge '✓' not found in Edit Mode!");
  }

  await page.screenshot({ path: path.join(screenshotsDir, 'step2_edit_mode_badge.png') });
  console.log('📸 Saved screenshot: step2_edit_mode_badge.png');

  // Step 3: Test Empty State in Dictation
  console.log('\n🔍 Step 3: Testing Friendly Empty State in Dictation...');
  // Mark all target words as active in FSRS
  await page.evaluate(async () => {
    const { db } = await import('/src/db/dexie.ts');
    const lq = await db.learning_queue.toArray();
    for (const item of lq) {
      if (item.base_form) {
        await db.fsrs_progress.put({
          word_id: item.base_form.toLowerCase(),
          course_id: 'sfid',
          state: 1,
          due: new Date(),
          stability: 2,
          difficulty: 5,
          elapsed_days: 0,
          scheduled_days: 1,
          reps: 1,
          lapses: 0,
          last_review: new Date()
        });
      }
    }
  });

  // Navigate to Dictation
  await page.goto('http://localhost:5173/dictation/sfid', { waitUntil: 'networkidle2' });
  await new Promise(r => setTimeout(r, 1500));

  const promptText = await page.evaluate(() => {
    const el = document.querySelector('#english-prompt');
    return el ? el.textContent.trim() : '';
  });
  console.log(`- Dictation Empty State Title: "${promptText}"`);
  if (!promptText.includes('All words in this lesson are already in your FSRS review schedule')) {
    throw new Error(`FAIL: Expected friendly FSRS empty state, got "${promptText}"`);
  }

  await page.screenshot({ path: path.join(screenshotsDir, 'step3_empty_state.png') });
  console.log('📸 Saved screenshot: step3_empty_state.png');

  // Step 4: Test Review Mode Hint Consistency (System Word vs Custom Word)
  console.log('\n🔍 Step 4: Testing Review Mode Hint Consistency (System vs Custom word)...');
  await page.evaluate(async () => {
    const { db } = await import('/src/db/dexie.ts');
    await db.fsrs_progress.clear();
    await db.custom_dictionary.clear();

    // 1 System word
    await db.fsrs_progress.put({
      word_id: 'till',
      course_id: 'sfid',
      state: 1,
      due: new Date(Date.now() - 100000),
      stability: 2,
      difficulty: 5,
      elapsed_days: 0,
      scheduled_days: 1,
      reps: 1,
      lapses: 0,
      last_review: new Date()
    });

    // 1 Custom word with course_id and sentence_id only
    await db.custom_dictionary.add({
      base_form: 'mycustom',
      word_in_sentence: 'mycustom',
      en_translation: 'my custom definition',
      contextual_en: 'my custom definition',
      stage_id: 'stage_11',
      article_id: 'art_49',
      sentence_id: 'art_49_s001',
      course_id: 'sfid',
      synced: true
    });
    await db.fsrs_progress.put({
      word_id: 'mycustom',
      course_id: 'sfid',
      state: 1,
      due: new Date(Date.now() - 100000),
      stability: 2,
      difficulty: 5,
      elapsed_days: 0,
      scheduled_days: 1,
      reps: 1,
      lapses: 0,
      last_review: new Date()
    });
  });

  // Switch to Review Mode by clicking the toggle button in Layout header
  await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('.toggle-option'));
    const revBtn = btns.find(b => b.textContent && b.textContent.includes('Review'));
    if (revBtn) revBtn.click();
  });
  await new Promise(r => setTimeout(r, 1500));

  // Log Review Mode State
  const reviewState = await page.evaluate(() => {
    const statsEl = document.querySelector('#progress-stats');
    const inputEl = document.querySelector('#spell-input');
    const promptEl = document.querySelector('#english-prompt');
    return {
      stats: statsEl ? statsEl.textContent.trim() : null,
      inputDisabled: inputEl ? inputEl.disabled : null,
      inputPlaceholder: inputEl ? inputEl.placeholder : null,
      promptText: promptEl ? promptEl.textContent.trim() : null
    };
  });
  console.log('Review Mode State before typing:', JSON.stringify(reviewState, null, 2));

  // Helper to submit answer in test
  async function submitAnswer(text) {
    await page.evaluate((val) => {
      const input = document.querySelector('#spell-input');
      if (input) {
        input.focus();
        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
        nativeInputValueSetter.call(input, val);
        input.dispatchEvent(new Event('input', { bubbles: true }));
      }
    }, text);
    await new Promise(r => setTimeout(r, 150));
    await page.keyboard.press('Enter');
    await new Promise(r => setTimeout(r, 500));
  }

  // --- CARD 1 (System word: 'till') ---
  console.log('\n--- Testing Card 1 (System word: till) ---');

  // Error 1
  await submitAnswer('wrong1');

  // Error 2: English definition should appear
  await submitAnswer('wrong2');

  const defHint1 = await page.evaluate(() => {
    const el = document.querySelector('#hint-display');
    return el ? el.textContent.trim() : '';
  });
  console.log(`- Card 1 (2 errors) Definition Hint: "${defHint1}"`);
  if (!defHint1) {
    throw new Error('FAIL: Definition hint not displayed after 2 wrong attempts for Card 1!');
  }

  // Error 3: Masked example sentence should appear
  await submitAnswer('wrong3');

  const sentenceHint1 = await page.evaluate(() => {
    const el = document.querySelector('#sentence-hint-display');
    return el ? el.textContent.trim() : '';
  });
  console.log(`- Card 1 (3 errors) Masked Example Sentence: "${sentenceHint1}"`);
  if (!sentenceHint1) {
    throw new Error('FAIL: Masked example sentence not displayed after 3 wrong attempts for Card 1!');
  }
  await page.screenshot({ path: path.join(screenshotsDir, 'step4_card1_hint.png') });

  // Reveal Card 1: Full example sentence should appear
  const revealBtn = await page.$('#reveal-btn');
  if (revealBtn) {
    await revealBtn.click();
    await new Promise(r => setTimeout(r, 500));
  }
  const fullSentence1 = await page.evaluate(() => {
    const el = document.querySelector('#sentence-display');
    return el ? el.textContent.trim() : '';
  });
  console.log(`- Card 1 (Revealed) Full Example Sentence: "${fullSentence1}"`);
  if (!fullSentence1) {
    throw new Error('FAIL: Full example sentence not displayed on reveal for Card 1!');
  }
  await page.screenshot({ path: path.join(screenshotsDir, 'step4_card1_revealed.png') });

  // Proceed to Card 2
  await page.keyboard.press('Enter');
  await new Promise(r => setTimeout(r, 1200));

  // --- CARD 2 (Custom word: 'mycustom') ---
  console.log('\n--- Testing Card 2 (Custom word: mycustom) ---');

  // Error 1
  await submitAnswer('wrong1');

  // Error 2: English definition should appear
  await submitAnswer('wrong2');

  const defHint2 = await page.evaluate(() => {
    const el = document.querySelector('#hint-display');
    return el ? el.textContent.trim() : '';
  });
  console.log(`- Card 2 (2 errors) Definition Hint: "${defHint2}"`);
  if (!defHint2) {
    throw new Error('FAIL: Definition hint not displayed after 2 wrong attempts for Card 2!');
  }

  // Error 3: Masked example sentence should appear
  await submitAnswer('wrong3');

  const sentenceHint2 = await page.evaluate(() => {
    const el = document.querySelector('#sentence-hint-display');
    return el ? el.textContent.trim() : '';
  });
  console.log(`- Card 2 (3 errors) Masked Example Sentence: "${sentenceHint2}"`);
  if (!sentenceHint2) {
    throw new Error('FAIL: Masked example sentence not displayed after 3 wrong attempts for Card 2!');
  }
  await page.screenshot({ path: path.join(screenshotsDir, 'step4_card2_hint.png') });

  // Reveal Card 2: Full example sentence should appear
  const revealBtn2 = await page.$('#reveal-btn');
  if (revealBtn2) {
    await revealBtn2.click();
    await new Promise(r => setTimeout(r, 500));
  }
  const fullSentence2 = await page.evaluate(() => {
    const el = document.querySelector('#sentence-display');
    return el ? el.textContent.trim() : '';
  });
  console.log(`- Card 2 (Revealed) Full Example Sentence: "${fullSentence2}"`);
  if (!fullSentence2) {
    throw new Error('FAIL: Full example sentence not displayed on reveal for Card 2!');
  }
  await page.screenshot({ path: path.join(screenshotsDir, 'step4_card2_revealed.png') });

  console.log('\n🎉 ALL 4 E2E TESTS PASSED WITH 100% ACCURACY & CONSISTENCY!');
  await browser.close();
}

run().catch(err => {
  console.error('\n❌ E2E RUN FAILED:', err);
  process.exit(1);
});
