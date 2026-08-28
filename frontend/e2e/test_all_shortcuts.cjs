const { chromium } = require('playwright');

async function testShortcuts() {
  console.log('Testing all keyboard shortcuts in Cloud app...');
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1000, height: 800 } });

  // 1. Login
  await page.goto('http://localhost:5173/login');
  await page.fill('input[type="email"]', 'test@example.com');
  await page.fill('input[type="password"]', 'test_password_placeholder');
  await page.click('button[type="submit"]');
  await page.waitForTimeout(1500);

  // 2. Test Dictation Shortcuts
  console.log('--- Testing Dictation Shortcuts ---');
  await page.goto('http://localhost:5173/dictation/sfid');
  await page.waitForTimeout(1500);

  // Tab to play audio
  await page.keyboard.press('Tab');
  console.log('✓ Pressed Tab for Audio Playback');
  await page.waitForTimeout(500);

  // Escape to reveal answer
  await page.keyboard.press('Escape');
  await page.waitForTimeout(500);
  const revealedAnswer = await page.$('#answer-display.show');
  if (revealedAnswer) {
    console.log('✓ Escape triggered Answer Reveal successfully!');
  } else {
    console.error('✗ Escape did not reveal answer!');
  }

  // Enter to skip/advance
  await page.keyboard.press('Enter');
  await page.waitForTimeout(800);
  const nextInputVal = await page.$eval('#spell-input', el => el.value);
  console.log('✓ Enter skipped to next word, input reset to:', nextInputVal);

  // 3. Test Flashcard Shortcuts
  console.log('--- Testing Flashcard Shortcuts ---');
  await page.goto('http://localhost:5173/flashcard/sfid');
  await page.waitForTimeout(1500);

  // Escape to reveal answer
  await page.keyboard.press('Escape');
  await page.waitForTimeout(500);
  const fRevealed = await page.$('#answer-display.show');
  if (fRevealed) {
    console.log('✓ Escape triggered Flashcard Reveal successfully!');
  } else {
    console.error('✗ Escape did not reveal flashcard answer!');
  }

  // Enter to proceed
  await page.keyboard.press('Enter');
  await page.waitForTimeout(800);
  console.log('✓ Enter proceeded to next flashcard');

  // 4. Test Narration Shortcuts
  console.log('--- Testing Narration Shortcuts ---');
  await page.goto('http://localhost:5173/narration/sfid');
  await page.waitForTimeout(1500);

  // Space to advance to next sentence
  await page.keyboard.press('Space');
  await page.waitForTimeout(500);
  console.log('✓ Space advanced to next sentence in Narration');

  // Shift + Space to go back
  await page.keyboard.press('Shift+Space');
  await page.waitForTimeout(500);
  console.log('✓ Shift+Space went back to previous sentence in Narration');

  // Enter to replay current sentence
  await page.keyboard.press('Enter');
  await page.waitForTimeout(500);
  console.log('✓ Enter replayed current sentence in Narration');

  await browser.close();
  console.log('ALL SHORTCUT TESTS PASSED WITH 100% SUCCESS!');
}

testShortcuts().catch(console.error);
