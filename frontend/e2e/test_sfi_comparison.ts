import { chromium } from 'playwright';
import * as path from 'path';
import * as fs from 'fs';

const SCREENSHOT_DIR = './reports/a5d1ee7a-3f21-4b48-8371-19932f1e650d';

async function main() {
  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 900 }
  });

  const page = await context.newPage();

  console.log('1. Navigating to SFI web_app: http://localhost:8080');
  await page.goto('http://localhost:8080', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'sfi_01_initial.png') });

  // Check stage select in SFI
  const stageSelect = page.locator('#stage-select, select').first();
  if (await stageSelect.count() > 0) {
    const stageOptions = await stageSelect.locator('option').allTextContents();
    console.log('SFI Stages:', stageOptions);
    const s12 = stageOptions.find(o => o.includes('12') || o.includes('Blandade'));
    if (s12) {
      await stageSelect.selectOption({ label: s12 });
      await page.waitForTimeout(1000);
    }
  }

  // Check article select
  const articleSelect = page.locator('#article-select, select').nth(1);
  if (await articleSelect.count() > 0) {
    const articleOptions = await articleSelect.locator('option').allTextContents();
    console.log('SFI Articles:', articleOptions);
    const art58 = articleOptions.find(o => o.includes('art_58') || o.includes('58'));
    if (art58) {
      await articleSelect.selectOption({ label: art58 });
    } else if (articleOptions.length > 0) {
      await articleSelect.selectOption({ index: 0 });
    }
    await page.waitForTimeout(1000);
  }

  await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'sfi_02_article_loaded.png') });

  // Find first sentence card
  const firstCard = page.locator('.sentence-card').first();
  await firstCard.scrollIntoViewIfNeeded();

  // Enter edit mode
  await firstCard.hover();
  const editBtn = firstCard.locator('.extract-vocab-btn');
  if (await editBtn.count() > 0) {
    console.log('Clicking SFI extract-vocab-btn...');
    await editBtn.click();
    await page.waitForTimeout(300);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'sfi_03_edit_mode_karaoke.png') });
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'sfi_04_edit_mode_ready.png') });

    // Inspect selectable words in SFI
    const sfiWords = await page.evaluate(() => {
      const card = document.querySelector('.sentence-card.edit-mode');
      if (!card) return null;
      return Array.from(card.querySelectorAll('.selectable-word')).map(w => ({
        text: w.textContent?.trim(),
        classes: w.className
      }));
    });
    console.log('SFI Words in Edit Mode:', sfiWords);

    // Toggle a word
    const targetWord = firstCard.locator('.selectable-word.selected-word').first();
    if (await targetWord.count() > 0) {
      const txt = await targetWord.textContent();
      console.log('Deselecting SFI target word:', txt);
      await targetWord.click();
      await page.waitForTimeout(300);
      await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'sfi_05_target_deselected_save_visible.png') });

      console.log('Re-selecting SFI target word:', txt);
      await targetWord.click();
      await page.waitForTimeout(300);
      await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'sfi_06_target_reselected_save_hidden.png') });
    }

    // Click plain word with unknown translation
    const words = firstCard.locator('.selectable-word');
    const cnt = await words.count();
    for (let i = 0; i < cnt; i++) {
      const w = words.nth(i);
      const isSelected = await w.evaluate(el => el.classList.contains('selected-word') || el.classList.contains('selected-secondary-word'));
      if (!isSelected) {
        await w.click();
        await page.waitForTimeout(200);
        const isUnknown = await w.evaluate(el => el.classList.contains('selected-unknown-word'));
        if (isUnknown) {
          console.log(`SFI word ${i} marked as unknown`);
          break;
        }
      }
    }
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'sfi_07_unknown_word_selected.png') });

    // Click Save Changes in SFI
    const saveBtn = firstCard.locator('.save-vocab-btn, #save-btn, button:has-text("Save")');
    if (await saveBtn.count() > 0) {
      await saveBtn.first().click();
      await page.waitForTimeout(800);
      await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'sfi_08_missing_translation_modal.png') });
    }
  }

  await browser.close();
  console.log('SFI comparison test finished!');
}

main().catch(err => {
  console.error('SFI test failed:', err);
  process.exit(1);
});
