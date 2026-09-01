const fs = require('fs');

function fixDeps(file) {
  let code = fs.readFileSync(file, 'utf8');
  // Remove learningQueue from dependency array
  code = code.replace(
    /}, \[courseId, appMode, selectedArticleId, learningQueue\]\);/g,
    '}, [courseId, appMode, selectedArticleId]); // deliberately omit learningQueue to prevent mid-session resets'
  );
  
  // Remove the bug toast
  code = code.replace(
    /window\.dispatchEvent\(new CustomEvent\('fsrs-toast', \{ detail: \`BUG: \$\{wordId\} not in \$\{selectedArticleId\}\` \}\)\);/g,
    '// removed bug toast'
  );

  fs.writeFileSync(file, code);
}

fixDeps('frontend/src/pages/Dictation.tsx');
fixDeps('frontend/src/pages/Flashcard.tsx');
