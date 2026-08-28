const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const ARTIFACT_DIR = './reports/a5d1ee7a-3f21-4b48-8371-19932f1e650d';

async function run() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1200, height: 900 } });
  
  // 1. Capture Legacy Dictation & Flashcard
  const pageL = await context.newPage();
  
  console.log('Capturing Legacy Dictation...');
  await pageL.goto('http://localhost:8000/dictation.html');
  await pageL.waitForTimeout(1000);
  // select sfid course if needed
  try {
    const courseBtn = await pageL.$('#course-selector-btn');
    if (courseBtn) {
      await courseBtn.click();
      await pageL.waitForTimeout(300);
      const sfidCard = await pageL.$('.course-card[data-course="sfid"]');
      if (sfidCard) await sfidCard.click();
      await pageL.waitForTimeout(500);
    }
  } catch (e) { console.log('Legacy course select error:', e.message); }
  
  // Select stage_01, art_00
  await pageL.selectOption('#stage-select', 'stage_01').catch(() => {});
  await pageL.waitForTimeout(300);
  await pageL.selectOption('#article-select', 'art_00').catch(() => {});
  await pageL.waitForTimeout(500);
  await pageL.screenshot({ path: path.join(ARTIFACT_DIR, 'legacy_dictation_initial.png') });
  
  console.log('Capturing Legacy Flashcard...');
  await pageL.goto('http://localhost:8000/flashcard.html');
  await pageL.waitForTimeout(1000);
  try {
    const courseBtn = await pageL.$('#course-selector-btn');
    if (courseBtn) {
      await courseBtn.click();
      await pageL.waitForTimeout(300);
      const sfidCard = await pageL.$('.course-card[data-course="sfid"]');
      if (sfidCard) await sfidCard.click();
      await pageL.waitForTimeout(500);
    }
  } catch (e) {}
  await pageL.selectOption('#stage-select', 'stage_01').catch(() => {});
  await pageL.waitForTimeout(300);
  await pageL.selectOption('#article-select', 'art_00').catch(() => {});
  await pageL.waitForTimeout(500);
  await pageL.screenshot({ path: path.join(ARTIFACT_DIR, 'legacy_flashcard_initial.png') });

  // 2. Capture Cloud Dictation & Flashcard
  const pageC = await context.newPage();
  console.log('Logging into Cloud...');
  await pageC.goto('http://localhost:5173/login');
  await pageC.waitForSelector('input[type="email"]', { timeout: 10000 });
  await pageC.fill('input[type="email"]', 'test@example.com');
  await pageC.fill('input[type="password"]', 'test_password_placeholder');
  await pageC.click('button[type="submit"]');
  await pageC.waitForTimeout(1500);
  
  console.log('Capturing Cloud Dictation...');
  await pageC.goto('http://localhost:5173/dictation/sfid');
  await pageC.waitForTimeout(1500);
  // select stage_01, art_00
  await pageC.selectOption('#stage-select', 'stage_01').catch(() => {});
  await pageC.waitForTimeout(300);
  await pageC.selectOption('#article-select', 'art_00').catch(() => {});
  await pageC.waitForTimeout(500);
  await pageC.screenshot({ path: path.join(ARTIFACT_DIR, 'cloud_dictation_initial.png') });

  console.log('Capturing Cloud Flashcard...');
  await pageC.goto('http://localhost:5173/flashcard/sfid');
  await pageC.waitForTimeout(1500);
  await pageC.selectOption('#stage-select', 'stage_01').catch(() => {});
  await pageC.waitForTimeout(300);
  await pageC.selectOption('#article-select', 'art_00').catch(() => {});
  await pageC.waitForTimeout(500);
  await pageC.screenshot({ path: path.join(ARTIFACT_DIR, 'cloud_flashcard_initial.png') });

  await browser.close();
  console.log('Screenshots captured successfully!');
}

run().catch(console.error);
