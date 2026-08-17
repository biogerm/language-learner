export function localParseSentence(svText: string, targetWords: any[] = [], secondaryWords: any[] = []) {
    let allWords: any[] = [];
    if (targetWords) {
        allWords.push(...targetWords.map(w => typeof w === 'string' ? { word: w, type: 'target' } : { ...w, type: 'target' }));
    }
    if (secondaryWords) {
        allWords.push(...secondaryWords.map(w => typeof w === 'string' ? { word: w, type: 'secondary' } : { ...w, type: 'secondary' }));
    }
    
    // Check if we have position data
    const hasPositions = allWords.length > 0 && allWords.every(w => w.position_start !== undefined && w.position_end !== undefined);
    
    if (hasPositions) {
        allWords.sort((a, b) => a.position_start - b.position_start);
        let htmlChunks: string[] = [];
        let currentIndex = 0;
        allWords.forEach(w => {
            if (w.position_start >= currentIndex) {
                htmlChunks.push(svText.substring(currentIndex, w.position_start));
                let exactWord = svText.substring(w.position_start, w.position_end);
                let baseWord = encodeURIComponent(w.base_form || w.word || exactWord);
                htmlChunks.push(`<span class="vocab-word ${w.type}-word" data-word="${baseWord}">${exactWord}</span>`);
                currentIndex = w.position_end;
            }
        });
        htmlChunks.push(svText.substring(currentIndex));
        return htmlChunks.join("");
    } else {
        // Regex replacement
        let processedText = svText;
        let tokens: {token: string, html: string}[] = [];
        allWords.sort((a, b) => {
            const aWord = a.word || a.base_form || '';
            const bWord = b.word || b.base_form || '';
            return bWord.length - aWord.length;
        });

        allWords.forEach((w, idx) => {
            const wordStr = w.word || w.base_form;
            if (!wordStr) return;
            let escaped = wordStr.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
            let regex = new RegExp(`\\b${escaped}\\b`, 'i');
            if (!regex.test(processedText)) {
                regex = new RegExp(escaped, 'i');
            }
            let match = processedText.match(regex);
            while (match) {
                let token = `__TOKEN_${idx}_${Math.random().toString(36).substring(7)}__`;
                let baseWord = encodeURIComponent(w.base_form || wordStr);
                tokens.push({ token, html: `<span class="vocab-word ${w.type}-word" data-word="${baseWord}">${match[0]}</span>` });
                processedText = processedText.replace(regex, token);
                match = processedText.match(regex);
            }
        });

        tokens.forEach(t => {
            processedText = processedText.replace(t.token, t.html);
        });

        return processedText;
    }
}
