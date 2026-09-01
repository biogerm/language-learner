const fs = require('fs');

function removeToast(file) {
  let code = fs.readFileSync(file, 'utf8');
  code = code.replace(
    /window\.dispatchEvent\(new CustomEvent\('fsrs-toast', \{ detail: \`BUG: \$\{wordId\} not in \$\{selectedArticleId\}\` \}\)\);/g,
    '// removed bug toast'
  );
  fs.writeFileSync(file, code);
}

removeToast('frontend/src/pages/Dictation.tsx');
removeToast('frontend/src/pages/Flashcard.tsx');
