import json, glob, re, sqlite3

# We know the 33 words
conn = sqlite3.connect('course/sfid/phase3/output/b1_vocab.db.bak') # backup still has the 38 missing words context
# wait, I can just use the words directly
words = [
    'badrum', 'kvart', 'paraply', 'ta det lugnt', 'Varför', 'emellan', 'faktisk', 'baddräkt',
    'komma tillbaka', 'i mitten av', 'ge', 'katalog', 'än', 'råna', 'bil', 'vara nere på',
    'krocka', 'träd', 'stå på menyn', 'trafikolycka', 'militär', 'släppa ut', 'prov', 'själ',
    'rymma', 'rå', 'vit', 'skjuten', '10 år gammal', 'för några dagar sedan', 'bör', 'hela dagen', 'detalj'
]

patterns = {w: re.compile(r'\b' + re.escape(w.lower()).replace('…', '.*') + r'\b', re.IGNORECASE) for w in words}
articles = glob.glob('course/sfid/phase2/articles_translated/art_*.json')

case_b = {}

for a_path in articles:
    with open(a_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for s in data.get('sentences', []):
            sv = s.get('sv', '')
            tws = s.get('target_words', [])
            
            for w in words:
                if patterns[w].search(sv):
                    # check if the word is somewhat inside the base_form or word_in_sentence
                    # or if one of the base_forms is inside the word
                    for tw in tws:
                        bf = tw.get('base_form', '').lower()
                        wis = tw.get('word_in_sentence', '').lower()
                        wl = w.lower()
                        
                        # Conditions for Case B:
                        # 1. The target word's base form contains the dictionary word (e.g. 'i detalj' contains 'detalj')
                        # 2. The dictionary word contains the target word's base form (e.g. 'hela dagen' contains 'hela')
                        # 3. Similar substring match indicating a tagging deviation, rather than a completely unrelated word.
                        
                        is_related = False
                        if wl in bf or bf in wl:
                            # prevent trivial matches like 'i' in 'i mitten av'
                            if len(bf) > 2 and len(wl) > 2:
                                is_related = True
                            
                        # If related but not exact match
                        if is_related and bf != wl:
                            if w not in case_b:
                                case_b[w] = []
                            # avoid duplicates
                            entry = f"Dict: '{w}' -> LLM Tagged: base_form='{bf}', word_in_sentence='{wis}'"
                            if entry not in case_b[w]:
                                case_b[w].append(entry)

for w in case_b:
    print(f"\n[{w}]")
    for b in case_b[w]:
        print(f"  {b}")

