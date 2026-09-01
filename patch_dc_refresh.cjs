const fs = require('fs');
let code = fs.readFileSync('frontend/src/contexts/DataContext.tsx', 'utf8');

code = code.replace(
  '        window.dispatchEvent(new CustomEvent("fsrs-toast", { detail: "☁️ Sync Complete" }));\n    }',
  '        window.dispatchEvent(new CustomEvent("fsrs-toast", { detail: "☁️ Sync Complete" }));\n        refreshLearningQueue();\n    }'
);

fs.writeFileSync('frontend/src/contexts/DataContext.tsx', code);
