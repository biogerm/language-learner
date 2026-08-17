import json, glob, re, sqlite3

conn = sqlite3.connect('course/sfid/phase3/output/b1_vocab.db')
cursor = conn.cursor()
cursor.execute("SELECT word FROM b1_vocabulary WHERE source='System'")
words = [row[0] for row in cursor.fetchall()]
conn.close()

patterns = {w: re.compile(r'\b' + re.escape(w.lower()).replace('…', '.*') + r'\b', re.IGNORECASE) for w in words}
articles = glob.glob('course/sfid/phase2/articles_translated/art_*.json')

matches = {w: [] for w in words}

for a_path in articles:
    with open(a_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for s in data.get('sentences', []):
            sv = s.get('sv', '')
            for w in words:
                if patterns[w].search(sv):
                    # Check if it is in target_words (maybe under a different base_form)
                    tws = s.get('target_words', [])
                    tw_words = [tw.get('word_in_sentence', '').lower() for tw in tws]
                    base_forms = [tw.get('base_form', '').lower() for tw in tws]
                    matches[w].append({
                        'sentence': sv,
                        'audio': s.get('audio_filename'),
                        'source': data.get('title'),
                        'target_words': tw_words,
                        'base_forms': base_forms
                    })

for w in words:
    if matches[w]:
        print(f"WORD: {w}")
        for m in matches[w]:
            print(f"  Sentence: {m['sentence']}")
            print(f"  Tagged base_forms: {m['base_forms']}")
            print(f"  Tagged word_in_sentence: {m['target_words']}")
            break # Just show the first match for brevity
