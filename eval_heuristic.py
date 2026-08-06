import re
import json

def normalize(s):
    return re.sub(r'[^\w\s]', '', s.lower())

discrepancies = []
with open('./course/sfid/phase2/prompts/eval_prompt.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

current_sv = ""
current_en = ""
current_id = ""

for line in lines:
    line = line.strip()
    if line.startswith('--- '):
        current_id = line.replace('---', '').strip()
    elif line.startswith('sv:'):
        current_sv = line[3:].strip()
    elif line.startswith('en:'):
        current_en = line[3:].strip()
    elif line.startswith('Word:'):
        parts = line.split('|')
        if len(parts) == 3:
            word = parts[0].replace('Word:', '').strip()
            contextual_en = parts[1].replace('contextual_en:', '').strip()
            master_en = parts[2].replace('master_en:', '').strip()
            
            discrepancies.append({
                'id': current_id,
                'sv': current_sv,
                'en': current_en,
                'word': word,
                'contextual_en': contextual_en,
                'master_en': master_en
            })

print(f"Parsed {len(discrepancies)} discrepancies.")

truly_wrong = []
for d in discrepancies:
    sv_norm = normalize(d['sv'])
    word_norm = normalize(d['word'])
    
    # Heuristic 1: The word is not in the sv sentence at all (hallucinated mapping)
    if word_norm not in sv_norm:
        # Check if it's just a lemmatization issue, e.g. "skrapa" vs "skrapar"
        # We can do a loose check: is the word_norm a substring of any word in sv_norm?
        # Or is any word in sv_norm a substring of word_norm?
        found = False
        sv_words = sv_norm.split()
        for w in sv_words:
            if word_norm in w or w in word_norm:
                if len(w) > 2 and len(word_norm) > 2:
                    found = True
                    break
        if not found:
            truly_wrong.append(f"{d['id']}:::{d['word']}")
            continue
            
with open('heuristic_wrong.json', 'w', encoding='utf-8') as f:
    json.dump(truly_wrong, f, indent=2, ensure_ascii=False)

print(f"Found {len(truly_wrong)} potentially wrong by heuristic 1.")
