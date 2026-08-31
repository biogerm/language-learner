const { chromium } = require('playwright');

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1000, height: 800 } });
  
  await p.goto('http://localhost:5173/login');
  await p.fill('input[type="email"]', 'test@example.com');
  await p.fill('input[type="password"]', process.env.TEST_USER_PASSWORD || 'test-password');
  await p.click('button[type="submit"]');
  await p.waitForTimeout(1500);

  // Switch to Review mode
  await p.goto('http://localhost:5173/dictation/sfid');
  await p.waitForTimeout(1000);
  const reviewToggle = await p.$('#fsrs-mode-toggle button:has-text("Review")');
  if (reviewToggle) await reviewToggle.click();
  await p.waitForTimeout(1000);
  await p.screenshot({ path: './screenshots/dictation_review_mode.png' });

  // Flashcard in Review mode
  await p.goto('http://localhost:5173/flashcard/sfid');
  await p.waitForTimeout(1000);
  await p.screenshot({ path: './screenshots/flashcard_review_mode.png' });

  console.log('Review modes captured successfully!');
  await b.close();
})();
