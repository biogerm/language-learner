const fs = require('fs');
let code = fs.readFileSync('frontend/src/contexts/DataContext.tsx', 'utf8');

code = code.replace(/syncUserData/g, 'syncLearningQueueRemote');
code = code.replace(
  'syncLearningQueueRemote: (isInitial?: boolean) => Promise<void>;',
  'syncLearningQueueRemote: () => Promise<void>;'
);
code = code.replace(
  'syncLearningQueueRemote: async () => {},',
  'syncLearningQueueRemote: async () => {},'
);

fs.writeFileSync('frontend/src/contexts/DataContext.tsx', code);

let dCode = fs.readFileSync('frontend/src/pages/Dictation.tsx', 'utf8');
dCode = dCode.replace(/syncUserData/g, 'syncLearningQueueRemote');
fs.writeFileSync('frontend/src/pages/Dictation.tsx', dCode);

let fCode = fs.readFileSync('frontend/src/pages/Flashcard.tsx', 'utf8');
fCode = fCode.replace(/syncUserData/g, 'syncLearningQueueRemote');
fs.writeFileSync('frontend/src/pages/Flashcard.tsx', fCode);
