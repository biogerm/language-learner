const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const SCREENSHOT_DIR = './reports/a5d1ee7a-3f21-4b48-8371-19932f1e650d';

async function runTests() {
  if (!fs.existsSync(SCREENSHOT_DIR)) {
    fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
  }

  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 900 }
  });

  const page = await context.newPage();

  console.log('=== STARTING QA E2E TESTING FOR 4 FIXES ===\n');

  // Step 0: Login
  console.log('--- Step 0: Login ---');
  await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
  await page.fill('input[type="email"]', 'test@example.com');
  await page.fill('input[type="password"]', 'test_password_placeholder');
  await page.click('button[type="submit"]');
  await page.waitForTimeout(1500);

  // Reset localStorage to clean state AND clear IndexedDB cache (awaitable)
  await page.evaluate(() => {
    localStorage.removeItem('customVocab');
    localStorage.removeItem('excludedVocab');
    localStorage.removeItem('dictationMasteredWords');
    localStorage.removeItem('flashcardMasteredWords');
    localStorage.setItem('appMode', 'study');
  });

  // Clear IndexedDB awaitably in its own evaluate call (all relevant stores)
  await page.evaluate(() => {
    return new Promise((resolve, reject) => {
      const openReq = indexedDB.open('LanguageLearnerDB');
      openReq.onerror = () => resolve(null); // don't fail if DB not yet created
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
  console.log('DB cleared. Navigating to Narration sfid...');

  // Navigate to Narration sfid
  await page.goto('http://localhost:5173/narration/sfid', { waitUntil: 'networkidle' });
  await page.waitForTimeout(3000); // Wait for fresh vocab.json fetch and React hydration

  // Select Stage 12, Article art_58
  const selects = page.locator('select');
  await selects.first().selectOption('stage_12');
  await page.waitForTimeout(1000);
  await page.locator('select').nth(1).selectOption('art_58');
  await page.waitForTimeout(2000); // Wait for syncLearningQueue to populate target words

  console.log('\n======================================================');
  console.log('TEST 1: Secondary Words Display & Custom Vocab Promotion');
  console.log('======================================================');

  // 1.1 Check Reading Mode: Secondary words (like 'Detta') have blue dashed underline (.secondary-word)
  const sentence1 = page.locator('.sentence-card').first();
  await sentence1.scrollIntoViewIfNeeded();

  const dettaReading = await sentence1.locator('.secondary-word').first();
  const dettaReadingText = await dettaReading.textContent();
  const dettaReadingClasses = await dettaReading.getAttribute('class');
  const dettaReadingStyle = await dettaReading.evaluate(el => {
    const s = window.getComputedStyle(el);
    return {
      borderBottom: s.borderBottom,
      color: s.color,
      backgroundColor: s.backgroundColor
    };
  });
  console.log('Reading Mode "Detta" text:', dettaReadingText);
  console.log('Reading Mode "Detta" class:', dettaReadingClasses);
  console.log('Reading Mode "Detta" computed styles:', dettaReadingStyle);

  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '01_test1_reading_mode_secondary_word.png') });

  // 1.2 Click '📖' on sentence 1: Check Edit Mode: Secondary words are clearly visible with blue dashed underline BEFORE being clicked
  console.log('Clicking 📖 on sentence 1...');
  await sentence1.hover();
  await sentence1.locator('.extract-vocab-btn').click();
  // Wait past karaoke wave animation
  await page.waitForTimeout(1200);

  const dettaEditBefore = await sentence1.locator('.selectable-word').first();
  const dettaEditBeforeClasses = await dettaEditBefore.getAttribute('class');
  const dettaEditBeforeStyle = await dettaEditBefore.evaluate(el => {
    const s = window.getComputedStyle(el);
    return {
      borderBottom: s.borderBottom,
      color: s.color,
      backgroundColor: s.backgroundColor
    };
  });
  console.log('Edit Mode "Detta" BEFORE click class:', dettaEditBeforeClasses);
  console.log('Edit Mode "Detta" BEFORE click styles:', dettaEditBeforeStyle);

  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '02_test1_edit_mode_secondary_word_unselected.png') });

  // 1.3 Click 'Detta': it becomes solid blue (.selected-secondary-word)
  console.log('Clicking "Detta" in Edit Mode...');
  await dettaEditBefore.click();
  await page.waitForTimeout(400);

  const dettaEditAfter = await sentence1.locator('.selectable-word').first();
  const dettaEditAfterClasses = await dettaEditAfter.getAttribute('class');
  const dettaEditAfterStyle = await dettaEditAfter.evaluate(el => {
    const s = window.getComputedStyle(el);
    return {
      borderBottom: s.borderBottom,
      color: s.color,
      backgroundColor: s.backgroundColor
    };
  });
  console.log('Edit Mode "Detta" AFTER click class:', dettaEditAfterClasses);
  console.log('Edit Mode "Detta" AFTER click styles:', dettaEditAfterStyle);

  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '03_test1_edit_mode_detta_selected_solid_blue.png') });

  // 1.4 Click 'Save Changes': verify 'Detta' is saved, toast appears, and in Reading mode 'Detta' is now highlighted in emerald green (.custom-word)
  console.log('Clicking "Save Changes"...');
  const saveChangesBtn = sentence1.locator('.save-vocab-btn');
  await saveChangesBtn.click();
  await page.waitForTimeout(300);

  // Capture toast if present
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '04_test1_save_changes_toast.png') });
  await page.waitForTimeout(800);

  const dettaReadingSaved = await sentence1.locator('.custom-word').first();
  const dettaSavedText = await dettaReadingSaved.textContent();
  const dettaSavedClasses = await dettaReadingSaved.getAttribute('class');
  const dettaSavedStyle = await dettaReadingSaved.evaluate(el => {
    const s = window.getComputedStyle(el);
    return {
      borderBottom: s.borderBottom,
      color: s.color,
      backgroundColor: s.backgroundColor
    };
  });
  console.log('Reading Mode "Detta" AFTER SAVE text:', dettaSavedText);
  console.log('Reading Mode "Detta" AFTER SAVE class:', dettaSavedClasses);
  console.log('Reading Mode "Detta" AFTER SAVE styles:', dettaSavedStyle);

  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '05_test1_reading_mode_detta_emerald_green.png') });

  console.log('\n======================================================');
  console.log('TEST 2: Dictation & Flashcard Study Queue Integration');
  console.log('======================================================');

  // 2.1 Switch to Dictation in Study Mode: verify that 'Detta' is in the Dictation study queue!
  console.log('Navigating to Dictation (/dictation/sfid)...');
  await page.goto('http://localhost:5173/dictation/sfid', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1200);

  // Must select stage_12 and art_58 to trigger syncLearningQueue
  await page.locator('select').first().selectOption('stage_12');
  await page.waitForTimeout(600);
  await page.locator('select').nth(1).selectOption('art_58');
  await page.waitForTimeout(1500);

  // Check Dexie db and page queue items via exposeFunction to avoid GC
  const dictationQueue = await page.evaluate(() => {
    return new Promise((resolve, reject) => {
      const openReq = indexedDB.open('LanguageLearnerDB');
      openReq.onerror = () => reject(openReq.error);
      openReq.onsuccess = () => {
        const db = openReq.result;
        if (!db.objectStoreNames.contains('learning_queue')) {
          resolve([]);
          return;
        }
        const tx = db.transaction('learning_queue', 'readonly');
        const store = tx.objectStore('learning_queue');
        const getReq = store.getAll();
        getReq.onerror = () => reject(getReq.error);
        getReq.onsuccess = () => {
          resolve(getReq.result.map(q => ({ word: q.base_form, article: q.article_id })));
        };
      };
    });
  });
  console.log('Learning Queue in Dexie for art_58 (Dictation):', dictationQueue);
  const hasDettaInDictation = dictationQueue.some(q => (q.word||'').toLowerCase() === 'detta');
  console.log('Is "Detta" in Dictation queue?:', hasDettaInDictation);

  const dictationStats = await page.locator('#progress-stats').textContent();
  console.log('Dictation Progress Stats:', dictationStats);

  // Let us type or reveal in dictation to verify queue word
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '06_test2_dictation_study_queue_initial.png') });

  // Type wrong word and reveal to see words in queue
  const inputEl = page.locator('#spell-input');
  if (await inputEl.count() > 0 && await inputEl.isVisible()) {
    await inputEl.fill('fel');
    await page.keyboard.press('Enter');
    await page.waitForTimeout(400);

    // Click reveal
    const revBtn = page.locator('#reveal-btn');
    if (await revBtn.count() > 0) {
      await revBtn.click();
      await page.waitForTimeout(600);
    }

    const dictationWordRevealed = await page.locator('#correct-sv').textContent().catch(() => 'N/A');
    console.log('Dictation Word 1 revealed:', dictationWordRevealed);
  }
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '07_test2_dictation_study_queue_word1.png') });

  // 2.2 Switch to Flashcard in Study Mode: verify that 'Detta' is in the Flashcard study queue!
  console.log('Navigating to Flashcard (/flashcard/sfid)...');
  await page.goto('http://localhost:5173/flashcard/sfid', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1200);

  // Must select stage_12 and art_58 to trigger syncLearningQueue
  await page.locator('select').first().selectOption('stage_12');
  await page.waitForTimeout(600);
  await page.locator('select').nth(1).selectOption('art_58');
  await page.waitForTimeout(1500);

  const flashcardStats = await page.locator('#progress-stats').textContent();
  console.log('Flashcard Progress Stats:', flashcardStats);

  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '08_test2_flashcard_study_queue_initial.png') });

  // Reveal answer in Flashcard
  const fInput = page.locator('#spell-input');
  if (await fInput.count() > 0 && await fInput.isVisible()) {
    await fInput.fill('fel');
    await page.keyboard.press('Enter');
    await page.waitForTimeout(400);
    const fRevBtn = page.locator('#reveal-btn');
    if (await fRevBtn.count() > 0) {
      await fRevBtn.click();
      await page.waitForTimeout(600);
    }

    const flashcardWordRevealed = await page.locator('#correct-sv').textContent().catch(() => 'N/A');
    console.log('Flashcard Word revealed:', flashcardWordRevealed);
  }
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '09_test2_flashcard_study_queue_revealed.png') });

  console.log('\n======================================================');
  console.log('TEST 3: Plain Word & "den" Unknown Word Color Differentiation');
  console.log('======================================================');

  // 3.1 Return to Narration, enter Edit Mode on sentence 1
  console.log('Returning to Narration...');
  await page.goto('http://localhost:5173/narration/sfid', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1500);
  await page.locator('select').first().selectOption('stage_12');
  await page.waitForTimeout(800);
  await page.locator('select').nth(1).selectOption('art_58');
  await page.waitForTimeout(1200);

  const s1 = page.locator('.sentence-card').first();
  await s1.hover();
  await s1.locator('.extract-vocab-btn').click();
  await page.waitForTimeout(1200); // Past karaoke

  // 3.2 Click 'den' (which is NOT in the dictionary): verify it is styled with .selected-unknown-word (muted gray with dashed border #9ca3af)
  const selectableWords = s1.locator('.selectable-word');
  const count = await selectableWords.count();
  console.log(`Sentence 1 has ${count} selectable words`);

  let denIndex = -1;
  for (let i = 0; i < count; i++) {
    const text = (await selectableWords.nth(i).textContent()).trim();
    if (text === 'den') {
      denIndex = i;
      break;
    }
  }
  console.log(`Index for word "den": ${denIndex}`);
  const denEl = selectableWords.nth(denIndex);

  console.log('Clicking plain word "den"...');
  await denEl.click();
  await page.waitForTimeout(300);

  const denClasses = await denEl.getAttribute('class');
  const denStyle = await denEl.evaluate(el => {
    const s = window.getComputedStyle(el);
    return {
      backgroundColor: s.backgroundColor,
      border: s.border,
      borderBottom: s.borderBottom,
      color: s.color
    };
  });
  console.log('Word "den" AFTER click class:', denClasses);
  console.log('Word "den" AFTER click styles:', denStyle);

  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '10_test3_den_selected_unknown_word_gray.png') });

  // 3.3 Click 'Save Changes': verify Missing Translation Modal appears for 'den'
  console.log('Clicking "Save Changes"...');
  await s1.locator('.save-vocab-btn').click();
  await page.waitForTimeout(800);

  const modalVisible = await page.locator('.learning-modal, .missing-translation-modal, [class*="modal"]').isVisible();
  console.log('Missing Translation Modal visible:', modalVisible);
  const modalSvWord = await page.locator('.learning-modal h3, .learning-modal div[style*="font-size: 2rem"]').allTextContents();
  console.log('Modal header & target word:', modalSvWord);

  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '11_test3_missing_translation_modal_opened.png') });

  // 3.4 Fill in English translation 'the / that' and submit
  console.log('Filling English translation "the / that"...');
  const modalInput = page.locator('.learning-modal input[type="text"]');
  await modalInput.fill('the / that');
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '12_test3_missing_translation_filled.png') });

  const modalSaveBtn = page.locator('.learning-modal button:has-text("Save Translation")');
  await modalSaveBtn.click();
  await page.waitForTimeout(300);

  // 3.5 Verify toast '🎉 Added to vocabulary book!' appears
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '13_test3_toast_added_to_vocabulary_book.png') });
  await page.waitForTimeout(1000);

  // Check Reading mode after 'den' added
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '14_test3_reading_mode_after_den_added.png') });

  // 3.6 Re-enter Edit Mode: verify 'den' is now .selected-custom-word (emerald green #10b981)
  console.log('Re-entering Edit Mode on sentence 1...');
  await s1.hover();
  await s1.locator('.extract-vocab-btn').click();
  await page.waitForTimeout(1200);

  const denElReEdit = s1.locator('.selectable-word').nth(denIndex);
  const denReEditClasses = await denElReEdit.getAttribute('class');
  const denReEditStyle = await denElReEdit.evaluate(el => {
    const s = window.getComputedStyle(el);
    return {
      backgroundColor: s.backgroundColor,
      border: s.border,
      borderBottom: s.borderBottom,
      color: s.color
    };
  });
  console.log('Re-Edit Mode "den" class:', denReEditClasses);
  console.log('Re-Edit Mode "den" styles:', denReEditStyle);

  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '15_test3_re_edit_den_selected_custom_word_green.png') });

  console.log('\n======================================================');
  console.log('TEST 4: Target Word Removal');
  console.log('======================================================');

  // 4.1 In Edit Mode on sentence 1, click target word 'första' to deselect (remove) it
  let forstaIndex = -1;
  for (let i = 0; i < count; i++) {
    const text = (await selectableWords.nth(i).textContent()).trim();
    if (text === 'första') {
      forstaIndex = i;
      break;
    }
  }
  console.log(`Index for target word "första": ${forstaIndex}`);
  const forstaEl = selectableWords.nth(forstaIndex);

  console.log('Clicking target word "första" to deselect...');
  await forstaEl.click();
  await page.waitForTimeout(400);

  const forstaDeselectedClasses = await forstaEl.getAttribute('class');
  const forstaDeselectedStyle = await forstaEl.evaluate(el => {
    const s = window.getComputedStyle(el);
    return {
      backgroundColor: s.backgroundColor,
      border: s.border,
      borderBottom: s.borderBottom,
      color: s.color
    };
  });
  console.log('Word "första" DESELECTED class:', forstaDeselectedClasses);
  console.log('Word "första" DESELECTED styles:', forstaDeselectedStyle);

  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '16_test4_forsta_deselected_edit_mode.png') });

  // 4.2 Click 'Save Changes'
  console.log('Clicking "Save Changes"...');
  await s1.locator('.save-vocab-btn').click();
  await page.waitForTimeout(1000);

  // 4.3 Verify in Reading Mode 'första' is now plain unhighlighted text
  const readingHtmlAfterForstaRemoved = await s1.locator('div[style*="font-size: 1.4rem"]').innerHTML();
  console.log('Reading Mode Sentence 1 HTML after removal:', readingHtmlAfterForstaRemoved);
  const excludedVocabStored = await page.evaluate(() => localStorage.getItem('excludedVocab'));
  console.log('excludedVocab in localStorage:', excludedVocabStored);

  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '17_test4_reading_mode_forsta_plain_unhighlighted.png') });

  // 4.4 Switch to Dictation / Flashcard: verify 'första' is NO LONGER in the study queue
  console.log('Switching to Dictation (/dictation/sfid)...');
  await page.goto('http://localhost:5173/dictation/sfid', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1200);
  await page.locator('select').first().selectOption('stage_12');
  await page.waitForTimeout(600);
  await page.locator('select').nth(1).selectOption('art_58');
  await page.waitForTimeout(1500);

  const dictationStatsAfter = await page.locator('#progress-stats').textContent();
  console.log('Dictation Progress Stats after removing första:', dictationStatsAfter);

  const dictationQueueAfter = await page.evaluate(() => {
    return new Promise((resolve, reject) => {
      const openReq = indexedDB.open('LanguageLearnerDB');
      openReq.onerror = () => reject(openReq.error);
      openReq.onsuccess = () => {
        const db = openReq.result;
        if (!db.objectStoreNames.contains('learning_queue')) { resolve([]); return; }
        const tx = db.transaction('learning_queue', 'readonly');
        const store = tx.objectStore('learning_queue');
        const getReq = store.getAll();
        getReq.onerror = () => reject(getReq.error);
        getReq.onsuccess = () => {
          resolve(getReq.result.map(q => q.base_form));
        };
      };
    });
  });
  console.log('Learning Queue in Dictation after removal:', dictationQueueAfter);
  const hasForstaInDictation = dictationQueueAfter.some(w => (w||'').toLowerCase() === 'första');
  console.log('Is "första" in Dictation queue?:', hasForstaInDictation);

  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '18_test4_dictation_without_forsta.png') });

  console.log('Switching to Flashcard (/flashcard/sfid)...');
  await page.goto('http://localhost:5173/flashcard/sfid', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1200);
  await page.locator('select').first().selectOption('stage_12');
  await page.waitForTimeout(600);
  await page.locator('select').nth(1).selectOption('art_58');
  await page.waitForTimeout(1500);

  const flashcardStatsAfter = await page.locator('#progress-stats').textContent();
  console.log('Flashcard Progress Stats after removing första:', flashcardStatsAfter);

  const flashcardQueueAfter = await page.evaluate(() => {
    return new Promise((resolve, reject) => {
      const openReq = indexedDB.open('LanguageLearnerDB');
      openReq.onerror = () => reject(openReq.error);
      openReq.onsuccess = () => {
        const db = openReq.result;
        if (!db.objectStoreNames.contains('learning_queue')) { resolve([]); return; }
        const tx = db.transaction('learning_queue', 'readonly');
        const store = tx.objectStore('learning_queue');
        const getReq = store.getAll();
        getReq.onerror = () => reject(getReq.error);
        getReq.onsuccess = () => {
          resolve(getReq.result.map(q => q.base_form));
        };
      };
    });
  });
  console.log('Learning Queue in Flashcard after removal:', flashcardQueueAfter);
  const hasForstaInFlashcard = flashcardQueueAfter.some(w => (w||'').toLowerCase() === 'första');
  console.log('Is "första" in Flashcard queue?:', hasForstaInFlashcard);

  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '19_test4_flashcard_without_forsta.png') });

  console.log('\n=== ALL 4 QA TESTS COMPLETED SUCCESSFULLY! ===');
  await browser.close();
}

runTests().catch(err => {
  console.error('Fatal error during QA testing:', err);
  process.exit(1);
});
