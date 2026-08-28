const { chromium } = require('playwright');

async function run() {
  const browser = await chromium.launch({ headless: true });
  
  // 1. Check Legacy App at port 8000
  const pageL = await browser.newPage();
  try {
    await pageL.goto('http://127.0.0.1:8000/dictation.html');
    const legacyState = await pageL.evaluate(() => {
      const fsrsData = localStorage.getItem('fsrsData');
      const vocabBook = localStorage.getItem('vocabBook');
      const customVocab = localStorage.getItem('customVocab');
      return {
        fsrsData: fsrsData ? JSON.parse(fsrsData) : null,
        vocabBook: vocabBook ? JSON.parse(vocabBook) : null,
        customVocab: customVocab ? JSON.parse(customVocab) : null
      };
    });
    console.log('--- LEGACY L-VERSION DATA ---');
    console.log('Legacy FSRS entries:', Object.keys(legacyState.fsrsData || {}).length, Object.keys(legacyState.fsrsData || {}));
    console.log('Legacy vocabBook:', legacyState.vocabBook);
    console.log('Legacy customVocab:', legacyState.customVocab);
  } catch (e) {
    console.log('Error querying legacy app:', e.message);
  }

  // 2. Check Supabase directly via Node
  await browser.close();
}

run().catch(console.error);
