const { chromium } = require('playwright');

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1000, height: 800 } });
  
  await p.goto('http://localhost:5173/login');
  await p.fill('input[type="email"]', 'test@example.com');
  await p.fill('input[type="password"]', 'test_password_placeholder');
  await p.click('button[type="submit"]');
  await p.waitForTimeout(1500);

  // 1. Dictation - Typing incorrect
  await p.goto('http://localhost:5173/dictation/sfid');
  await p.waitForTimeout(1500);
  await p.click('#spell-input');
  await p.fill('#spell-input', 'fel');
  await p.keyboard.press('Enter');
  await p.waitForTimeout(300);
  await p.screenshot({ path: './reports/a5d1ee7a-3f21-4b48-8371-19932f1e650d/dictation_incorrect_state.png' });

  // 2. Dictation - Reveal Answer
  await p.keyboard.press('Enter');
  await p.waitForTimeout(200);
  await p.keyboard.press('Enter');
  await p.waitForTimeout(200);
  const revBtn = await p.$('#reveal-btn');
  if (revBtn) await revBtn.click();
  await p.waitForTimeout(300);
  await p.screenshot({ path: './reports/a5d1ee7a-3f21-4b48-8371-19932f1e650d/dictation_revealed_state.png' });

  // 3. Flashcard - Typing incorrect
  await p.goto('http://localhost:5173/flashcard/sfid');
  await p.waitForTimeout(1500);
  await p.click('#spell-input');
  await p.fill('#spell-input', 'wrong');
  await p.keyboard.press('Enter');
  await p.waitForTimeout(300);
  await p.screenshot({ path: './reports/a5d1ee7a-3f21-4b48-8371-19932f1e650d/flashcard_incorrect_state.png' });

  // 4. Flashcard - Reveal Answer in Study mode
  const fRevBtn = await p.$('#reveal-btn');
  if (fRevBtn) await fRevBtn.click();
  await p.waitForTimeout(300);
  await p.screenshot({ path: './reports/a5d1ee7a-3f21-4b48-8371-19932f1e650d/flashcard_revealed_state.png' });

  // 5. Narration page verification
  await p.goto('http://localhost:5173/narration/sfid');
  await p.waitForTimeout(1500);
  await p.screenshot({ path: './reports/a5d1ee7a-3f21-4b48-8371-19932f1e650d/narration_verified.png' });

  console.log('All interaction states captured successfully!');
  await b.close();
})();
