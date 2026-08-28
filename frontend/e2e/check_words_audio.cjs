const http = require('http');

const words = ['detta', 'vara', 'den', 'första', 'testmening', 'här', 'komma', 'en', 'andra', 'mening', 'för', 'att', 'testa', 'snack'];

async function checkWord(w) {
  return new Promise((resolve) => {
    const enc = encodeURIComponent(w.toLowerCase());
    const req = http.get(`http://localhost:5173/api/r2/words_audio/${enc}.mp3`, (res) => {
      resolve({ word: w, status: res.statusCode });
    });
    req.on('error', (e) => resolve({ word: w, error: e.message }));
  });
}

async function run() {
  for (const w of words) {
    const res = await checkWord(w);
    console.log(`Word "${w}": HTTP ${res.status || res.error}`);
  }
}

run();
