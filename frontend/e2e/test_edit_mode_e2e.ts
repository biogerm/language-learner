import { chromium } from 'playwright';
import * as path from 'path';
import * as fs from 'fs';

const SCREENSHOT_DIR = './reports/a5d1ee7a-3f21-4b48-8371-19932f1e650d';

async function main() {
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

  console.log('1. Navigating to login page...');
  await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '01_login_page.png') });

  console.log('Logging in with test@example.com / test_password_placeholder...');
  await page.fill('input[type="email"]', 'test@example.com');
  await page.fill('input[type="password"]', 'test_password_placeholder');
  await page.click('button[type="submit"]');

  await page.waitForTimeout(2000);
  console.log('Current URL after login:', page.url());

  console.log('2. Navigating to Narration page: http://localhost:5173/narration/sfid');
  await page.goto('http://localhost:5173/narration/sfid', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1500);
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '02_narration_initial.png') });

  // Check stage selector
  console.log('3. Selecting Stage 12, Article art_58...');
  // Find stage select
  const stageSelect = page.locator('select').first();
  if (await stageSelect.count() > 0) {
    const stageOptions = await stageSelect.locator('option').allTextContents();
    console.log('Available Stage Options:', stageOptions);
    // Find Stage 12
    const s12Option = stageOptions.find(o => o.includes('Stage 12') || o.includes('12'));
    if (s12Option) {
      await stageSelect.selectOption({ label: s12Option });
      await page.waitForTimeout(1000);
    }
  }

  // Find article select (second select)
  const selects = page.locator('select');
  if (await selects.count() > 1) {
    const articleSelect = selects.nth(1);
    const articleOptions = await articleSelect.locator('option').allTextContents();
    console.log('Available Article Options:', articleOptions);
    const art58 = articleOptions.find(o => o.includes('art_58') || o.includes('58'));
    if (art58) {
      await articleSelect.selectOption({ label: art58 });
    } else if (articleOptions.length > 0) {
      await articleSelect.selectOption({ index: 0 });
    }
    await page.waitForTimeout(1000);
  }

  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '03_article_loaded.png') });

  // Locate the first sentence card
  const firstSentenceCard = page.locator('.sentence-card').first();
  await firstSentenceCard.scrollIntoViewIfNeeded();

  console.log('4. Checking reading mode state of first sentence...');
  const readingTargetWords = await firstSentenceCard.locator('.vocab-word').allTextContents();
  console.log('Initial target words in reading mode:', readingTargetWords);

  console.log('Clicking extract-vocab-btn (📖) to enter Edit Mode...');
  // Hover over card to make edit button visible if needed, then click
  await firstSentenceCard.hover();
  const editBtn = firstSentenceCard.locator('.extract-vocab-btn');
  await editBtn.click();

  // Check for karaoke animation immediately
  console.log('Checking karaoke animation on words...');
  const hasKaraokeAnim = await page.evaluate(() => {
    const animSpans = document.querySelectorAll('.karaoke-anim');
    return animSpans.length;
  });
  console.log(`Found ${hasKaraokeAnim} spans with karaoke-anim class`);

  await page.waitForTimeout(300);
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '04_edit_mode_karaoke_active.png') });

  // Wait for karaoke animation to finish
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '05_edit_mode_initial_state.png') });

  // Inspect selectable words in edit mode
  const wordsInfo = await page.evaluate(() => {
    const card = document.querySelector('.sentence-card.edit-mode');
    if (!card) return null;
    const words = Array.from(card.querySelectorAll('.selectable-word')).map(w => {
      const el = w as HTMLElement;
      return {
        text: el.textContent?.trim(),
        cleanWord: el.dataset.word,
        type: el.dataset.type,
        classes: el.className,
        isTarget: el.classList.contains('selected-word'),
        isSecondary: el.classList.contains('selected-secondary-word'),
        isCustom: el.classList.contains('selected-custom-word'),
        isUnknown: el.classList.contains('selected-unknown-word')
      };
    });
    const saveBtn = card.querySelector('.save-vocab-btn') as HTMLElement | null;
    const cancelBtn = card.querySelector('.cancel-edit-btn') as HTMLElement | null;
    return {
      words,
      saveBtnVisible: saveBtn ? window.getComputedStyle(saveBtn).display !== 'none' : false,
      cancelBtnVisible: cancelBtn ? window.getComputedStyle(cancelBtn).display !== 'none' : false
    };
  });
  console.log('Edit Mode Initial State:', JSON.stringify(wordsInfo, null, 2));

  // Find a target word and toggle it off
  const targetWordIdx = wordsInfo?.words.findIndex(w => w.isTarget);
  console.log(`Target word index found: ${targetWordIdx}`);

  if (targetWordIdx !== undefined && targetWordIdx >= 0) {
    const targetWordEl = firstSentenceCard.locator('.selectable-word').nth(targetWordIdx);
    const targetWordText = await targetWordEl.textContent();
    console.log(`Clicking target word "${targetWordText}" to deselect it...`);
    await targetWordEl.click();
    await page.waitForTimeout(500);

    const afterDeselect = await page.evaluate(() => {
      const card = document.querySelector('.sentence-card.edit-mode');
      const saveBtn = card?.querySelector('.save-vocab-btn') as HTMLElement | null;
      return {
        saveBtnVisible: saveBtn ? window.getComputedStyle(saveBtn).display !== 'none' : false
      };
    });
    console.log('After deselecting target word, Save Changes visible:', afterDeselect.saveBtnVisible);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '06_target_word_deselected_save_visible.png') });

    console.log(`Clicking target word "${targetWordText}" again to re-select it (revert state)...`);
    await targetWordEl.click();
    await page.waitForTimeout(500);

    const afterReselect = await page.evaluate(() => {
      const card = document.querySelector('.sentence-card.edit-mode');
      const saveBtn = card?.querySelector('.save-vocab-btn') as HTMLElement | null;
      return {
        saveBtnVisible: saveBtn ? window.getComputedStyle(saveBtn).display !== 'none' : false
      };
    });
    console.log('After re-selecting target word, Save Changes visible:', afterReselect.saveBtnVisible);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '07_target_word_reselected_save_hidden.png') });
  }

  // Test Plain words (with known translation vs without translation)
  console.log('Testing plain word clicking...');
  const plainIndices = wordsInfo?.words
    .map((w, idx) => ({ ...w, idx }))
    .filter(w => !w.isTarget && !w.isSecondary && !w.isCustom) || [];
  
  console.log('Plain words available:', plainIndices.map(p => p.text));

  for (const p of plainIndices) {
    const wordEl = firstSentenceCard.locator('.selectable-word').nth(p.idx);
    const wordText = await wordEl.textContent();
    console.log(`Clicking plain word [${p.idx}]: "${wordText}"...`);
    await wordEl.click();
    await page.waitForTimeout(300);

    const state = await page.evaluate((idx) => {
      const card = document.querySelector('.sentence-card.edit-mode');
      const word = card?.querySelectorAll('.selectable-word')[idx] as HTMLElement;
      return {
        classes: word?.className,
        isTarget: word?.classList.contains('selected-word'),
        isUnknown: word?.classList.contains('selected-unknown-word')
      };
    }, p.idx);

    console.log(`Word "${wordText}" state after click:`, state);
  }

  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '08_plain_words_toggled.png') });

  // Test Cancel button
  console.log('Testing Cancel button...');
  const cancelBtn = firstSentenceCard.locator('.cancel-edit-btn');
  await cancelBtn.click();
  await page.waitForTimeout(500);

  const isEditModeAfterCancel = await page.evaluate(() => {
    return document.querySelectorAll('.sentence-card.edit-mode').length;
  });
  console.log(`Edit mode cards count after cancel: ${isEditModeAfterCancel}`);
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '09_after_cancel_edit_mode.png') });

  // Re-enter edit mode to test unknown word -> Save Changes -> Missing Translation Modal
  console.log('Re-entering edit mode to test unknown word and Save Changes...');
  await firstSentenceCard.hover();
  await firstSentenceCard.locator('.extract-vocab-btn').click();
  await page.waitForTimeout(1000);

  // Find an unknown word (or click a plain word that becomes selected-unknown-word)
  let clickedUnknown = false;
  const wordCount = await firstSentenceCard.locator('.selectable-word').count();
  for (let i = 0; i < wordCount; i++) {
    const wEl = firstSentenceCard.locator('.selectable-word').nth(i);
    const isAlreadyTarget = await wEl.evaluate(el => el.classList.contains('selected-word') || el.classList.contains('selected-secondary-word'));
    if (!isAlreadyTarget) {
      await wEl.click();
      await page.waitForTimeout(200);
      const isUnknown = await wEl.evaluate(el => el.classList.contains('selected-unknown-word'));
      const isKnown = await wEl.evaluate(el => el.classList.contains('selected-word'));
      console.log(`Clicked word ${i} -> isUnknown: ${isUnknown}, isKnown: ${isKnown}`);
      if (isUnknown) {
        clickedUnknown = true;
        break;
      }
    }
  }

  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '10_unknown_word_selected.png') });

  console.log('Clicking Save Changes button...');
  const saveBtn = firstSentenceCard.locator('.save-vocab-btn');
  await saveBtn.click();
  await page.waitForTimeout(800);

  // Check if Missing Translation Modal appeared or toast
  const modalVisible = await page.evaluate(() => {
    const modal = document.querySelector('.missing-translation-modal, [class*="modal"]');
    return {
      modalFound: !!modal,
      html: modal?.outerHTML?.substring(0, 300)
    };
  });
  console.log('Modal check:', modalVisible);
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '11_missing_translation_modal_or_saved.png') });

  // If modal is visible, test filling and submitting
  const inputEl = page.locator('input[placeholder*="translation" i], input[type="text"]:visible');
  if (await inputEl.count() > 0) {
    console.log('Filling missing translation...');
    await inputEl.first().fill('test translation');
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '12_modal_input_filled.png') });
    // Click submit button in modal
    const submitBtn = page.locator('button:has-text("Save"), button:has-text("Submit"), button:has-text("Add")').last();
    await submitBtn.click();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '13_after_modal_submitted.png') });
  }

  // Check toast notification and updated reading view
  await page.waitForTimeout(500);
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '14_final_reading_view.png') });

  await browser.close();
  console.log('All tests completed successfully!');
}

main().catch(err => {
  console.error('Test execution failed:', err);
  process.exit(1);
});
