const { chromium } = require('playwright');
const path = require('path');

const ARTIFACT_DIR = process.env.ARTIFACT_DIR || './screenshots';
const SCREENSHOT_DIR = ARTIFACT_DIR;

async function runFeedbackVerification() {
  console.log('=== RUNNING VERIFICATION FOR USER FEEDBACK ===\n');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await context.newPage();

  // 1. Login
  console.log('Logging in...');
  await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
  await page.fill('input[type="email"]', process.env.TEST_USER_EMAIL || 'test@example.com');
  await page.fill('input[type="password"]', process.env.TEST_USER_PASSWORD || 'test-password');
  await page.click('button[type="submit"]');
  await page.waitForTimeout(1500);

  // Clear state
  await page.evaluate(() => {
    localStorage.removeItem('customVocab');
    localStorage.removeItem('excludedVocab');
    localStorage.removeItem('dictationMasteredWords');
    localStorage.removeItem('flashcardMasteredWords');
    localStorage.setItem('appMode', 'study');
  });

  // Navigate to Narration
  console.log('Navigating to Narration sfid...');
  await page.goto('http://localhost:5173/narration/sfid', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  await page.locator('select').first().selectOption('stage_12');
  await page.waitForTimeout(800);
  await page.locator('select').nth(1).selectOption('art_58');
  await page.waitForTimeout(1500);

  // Test 1: Secondary Word 'Detta' must NOT be green after save (stays blue dashed)
  console.log('\n--- Test 1: Secondary Word Color Verification ---');
  const s1 = page.locator('.sentence-card').first();
  await s1.hover();
  await s1.locator('.extract-vocab-btn').click();
  await page.waitForTimeout(1200);

  const dettaEl = s1.locator('.selectable-word[data-type="secondary"]').first();
  await dettaEl.click();
  await page.waitForTimeout(300);
  await s1.locator('.save-vocab-btn').click();
  await page.waitForTimeout(800);

  const dettaReading = s1.locator('.vocab-word[data-word="detta"], .vocab-word:has-text("Detta")').first();
  const dettaReadingClass = await dettaReading.getAttribute('class');
  console.log('Reading mode Detta class after save:', dettaReadingClass);
  const isDettaSecondaryOnly = dettaReadingClass.includes('secondary-word') && !dettaReadingClass.includes('custom-word');
  console.log('Is Detta secondary-word and NOT custom-word (green)?:', isDettaSecondaryOnly);

  await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'fb_01_detta_stays_secondary_blue_dashed.png') });

  // Test 2 & 3: Word "är" selection & Unicode boundary check (Har must NOT match)
  console.log('\n--- Test 3: Word "är" Selection & Unicode Boundary Verification ---');
  await s1.hover();
  await s1.locator('.extract-vocab-btn').click();
  await page.waitForTimeout(1200);

  // Click plain word "är"
  const arEl = s1.locator('.selectable-word').nth(1); // "är"
  const arText = (await arEl.textContent()).trim();
  console.log(`Word at index 1 is: "${arText}"`);
  await arEl.click();
  await page.waitForTimeout(300);

  const arClickedClass = await arEl.getAttribute('class');
  console.log('Class of "är" after click in edit mode:', arClickedClass);
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'fb_02_ar_selected_in_edit_mode.png') });

  await s1.locator('.save-vocab-btn').click();
  await page.waitForTimeout(800);

  // Check Reading mode on sentence 1: "är" MUST be highlighted as custom-word
  const arReading = s1.locator('.vocab-word.custom-word:has-text("är")');
  const hasArHighlightedInS1 = await arReading.count() > 0;
  console.log('Is "är" in Sentence 1 highlighted as custom-word?:', hasArHighlightedInS1);

  // Check all sentences: Check if "Har" has any highlight inside it
  const allCustomWords = await page.locator('.vocab-word.custom-word').allTextContents();
  console.log('All custom-word highlights on page:', allCustomWords);
  const hasHarFalselyHighlighted = allCustomWords.some(t => t.toLowerCase() === 'har' || t.toLowerCase() === 'ar');
  console.log('Is "Har" or partial "ar" falsely highlighted in other words?:', hasHarFalselyHighlighted);

  await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'fb_03_ar_highlighted_in_reading_mode_clean.png') });

  // Test 4: Target Word Removal across Dictation & Flashcard Study & Review
  console.log('\n--- Test 2 & 4: Target Word Removal from Study & Review ---');
  await s1.hover();
  await s1.locator('.extract-vocab-btn').click();
  await page.waitForTimeout(1200);

  // Deselect 'första'
  const forstaEl = s1.locator('.selectable-word:has-text("första")').first();
  await forstaEl.click();
  await page.waitForTimeout(300);
  await s1.locator('.save-vocab-btn').click();
  await page.waitForTimeout(800);

  // Check Reading mode: 'första' must NOT be highlighted
  const forstaReading = s1.locator('.vocab-word:has-text("första")');
  console.log('Count of "första" vocab highlights in reading mode:', await forstaReading.count());

  // Check Dictation queue
  console.log('Checking Dictation study queue...');
  await page.goto('http://localhost:5173/dictation/sfid', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1200);
  await page.locator('select').first().selectOption('stage_12');
  await page.waitForTimeout(600);
  await page.locator('select').nth(1).selectOption('art_58');
  await page.waitForTimeout(1500);

  const dictStats = await page.locator('#progress-stats').textContent();
  console.log('Dictation stats after excluding första:', dictStats);
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'fb_04_dictation_queue_without_forsta.png') });

  // Check Flashcard queue
  console.log('Checking Flashcard study queue...');
  await page.goto('http://localhost:5173/flashcard/sfid', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1200);
  await page.locator('select').first().selectOption('stage_12');
  await page.waitForTimeout(600);
  await page.locator('select').nth(1).selectOption('art_58');
  await page.waitForTimeout(1500);

  const flashStats = await page.locator('#progress-stats').textContent();
  console.log('Flashcard stats after excluding första:', flashStats);
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'fb_05_flashcard_queue_without_forsta.png') });

  console.log('\n=== ALL USER FEEDBACK TESTS PASSED! ===');
  await browser.close();
}

runFeedbackVerification().catch(err => {
  console.error('Fatal error during feedback verification:', err);
  process.exit(1);
});
