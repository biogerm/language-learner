const fs = require('fs');
let code = fs.readFileSync('frontend/package.json', 'utf8');

code = code.replace('"version": "2.2.3"', '"version": "2.2.4"');
code = code.replace('"dictation": "v2.2.30"', '"dictation": "v2.2.31"');
code = code.replace('"flashcard": "v2.2.34"', '"flashcard": "v2.2.35"');

fs.writeFileSync('frontend/package.json', code);
