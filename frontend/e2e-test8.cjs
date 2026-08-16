const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  
  try {
    await page.goto('http://localhost:5173/login', { waitUntil: 'networkidle0' });
    await page.type('input[type="email"]', 'test@example.com');
    await page.type('input[type="password"]', 'test_password_placeholder');
    await page.click('button[type="submit"]');
    
    await new Promise(r => setTimeout(r, 2000));
    
    // Dump IndexedDB
    const dexieData = await page.evaluate(async () => {
      return new Promise((resolve, reject) => {
        const request = indexedDB.open('LanguageLearnerDB');
        request.onsuccess = (event) => {
          const db = event.target.result;
          const transaction = db.transaction(['course_data'], 'readonly');
          const objectStore = transaction.objectStore('course_data');
          const getAllRequest = objectStore.getAll();
          
          getAllRequest.onsuccess = () => {
            resolve(getAllRequest.result);
          };
          getAllRequest.onerror = () => reject('Failed to get data');
        };
        request.onerror = () => reject('Failed to open db');
      });
    });
    
    console.log('DEXIE CACHE COURSE DATA COUNT:', dexieData.length);
    if (dexieData.length > 0) {
      console.log('Course IDs:', dexieData.map(d => d.courseId));
      console.log('Type of articles for sfid:', typeof dexieData.find(d => d.courseId === 'sfid')?.articles);
      const sfidData = dexieData.find(d => d.courseId === 'sfid');
      if (sfidData) {
        console.log('Keys of articles:', Object.keys(sfidData.articles).slice(0, 5));
        const firstStage = Object.keys(sfidData.articles)[0];
        console.log('Type of first stage:', typeof sfidData.articles[firstStage]);
        const firstArticle = Object.keys(sfidData.articles[firstStage] || {})[0];
        console.log('Type of first article sentences:', typeof sfidData.articles[firstStage][firstArticle]);
        if (typeof sfidData.articles[firstStage][firstArticle] === 'string') {
          console.log('Sample string data:', sfidData.articles[firstStage][firstArticle].substring(0, 100));
        }
      }
    }
  } catch(e) {
    console.error(e);
  } finally {
    await browser.close();
  }
})();
