export interface WordData {
    base_form?: string;
    position_start?: number;
    position_end?: number;
    type?: 'target' | 'secondary';
    contextual_en?: string;
    isExcluded?: boolean;
}

export function parseSentence(svText: string, targetWords: WordData[] = [], secondaryWords: WordData[] = []) {
    let allWords: WordData[] = [];
    if (targetWords) {
        allWords.push(...targetWords.map(w => ({ ...w, type: 'target' as const })));
    }
    if (secondaryWords) {
        allWords.push(...secondaryWords.map(w => ({ ...w, type: 'secondary' as const })));
    }
    
    allWords = allWords.filter(w => w.position_start !== undefined && w.position_end !== undefined);
    allWords.sort((a, b) => (a.position_start || 0) - (b.position_start || 0));
    
    let htmlChunks: string[] = [];
    let currentIndex = 0;
    
    allWords.forEach((w) => {
        if (w.position_start !== undefined && w.position_end !== undefined && w.position_start >= currentIndex) {
            htmlChunks.push(svText.substring(currentIndex, w.position_start));
            let exactWord = svText.substring(w.position_start, w.position_end);
            let baseWord = encodeURIComponent(w.base_form || exactWord);
            
            htmlChunks.push(`<span class="vocab-word ${w.type}-word" data-word="${baseWord}">${exactWord}</span>`);
            currentIndex = w.position_end;
        }
    });
    
    htmlChunks.push(svText.substring(currentIndex));
    return htmlChunks.join("");
}

export function parseEnglishSentence(enText: string, allWords: WordData[]) {
    let enWords = allWords.filter(w => w.contextual_en && !w.isExcluded).sort((a, b) => (b.contextual_en?.length || 0) - (a.contextual_en?.length || 0));
    let tokens: {token: string, html: string}[] = [];
    let processedEnText = enText;

    enWords.forEach((w, idx) => {
        if (!w.contextual_en) return;
        let escaped = w.contextual_en.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
        let regex = new RegExp(`\\b${escaped}\\b`, 'i');
        if (!regex.test(processedEnText)) {
            regex = new RegExp(escaped, 'i');
        }
        let match = processedEnText.match(regex);
        if (match) {
            let token = `__TOKEN_${idx}__`;
            tokens.push({ token: token, html: `<span class="vocab-word ${w.type}-word en-word">${match[0]}</span>` });
            processedEnText = processedEnText.replace(regex, token);
        }
    });

    tokens.forEach(t => {
        processedEnText = processedEnText.replace(t.token, t.html);
    });

    return processedEnText;
}
