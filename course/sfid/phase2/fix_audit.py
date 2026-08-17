import json
import os
import re
import glob

def find_best_match(base, sentence):
    # Try to find a word in sentence that starts with base
    words = re.findall(r'\b\w+\b', sentence, re.IGNORECASE)
    matches = [w for w in words if w.lower().startswith(base.lower())]
    if len(matches) == 1:
        return matches[0]
    
    # Try substring
    matches = [w for w in words if base.lower() in w.lower()]
    if len(matches) == 1:
        return matches[0]
        
    return None

def process():
    files = glob.glob('./course/sfid/phase2/articles_translated/*.json')
    for f in files:
        with open(f, 'r') as fp:
            data = json.load(fp)
            
        changed = False
        for s in data.get('sentences', []):
            sv = s['sv']
            for t in s.get('target_words', []) + s.get('secondary_words', []):
                word = t['word_in_sentence']
                # find occurrences
                occurrences = [m.start() for m in re.finditer(re.escape(word), sv, re.IGNORECASE)]
                if len(occurrences) != 1:
                    print(f"File: {os.path.basename(f)}, Sentence: {s['sentence_id']}, Word: {word}, Base: {t['base_form']}, Occurrences: {len(occurrences)}")
                    
                    if len(occurrences) == 0:
                        best = find_best_match(t['base_form'], sv)
                        if best:
                            print(f"  -> Best match: {best}")
                        else:
                            print(f"  -> Could not find match")
                    else:
                        print(f"  -> Need manual resolution for multiples")

process()
