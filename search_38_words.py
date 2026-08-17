import json, glob, re, sqlite3

conn = sqlite3.connect('course/sfid/phase3/output/b1_vocab.db')
cursor = conn.cursor()
cursor.execute("SELECT word FROM b1_vocabulary WHERE source='System'")
words = [row[0] for row in cursor.fetchall()]
conn.close()

# Prepare regex patterns
patterns = {}
for w in words:
    escaped = re.escape(w.lower())
    # Handle optional punctuation for phrases like "Har du hört talas om …?"
    escaped = escaped.replace('…', '.*')
    patterns[w] = re.compile(r'\b' + escaped + r'\b', re.IGNORECASE)

articles = glob.glob('course/sfid/phase2/articles_translated/art_*.json')
matches = {w: [] for w in words}

for a_path in articles:
    with open(a_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for idx, s in enumerate(data.get('sentences', [])):
            sv = s.get('sv', '')
            for w in words:
                if patterns[w].search(sv):
                    matches[w].append({
                        'article': a_path.split('/')[-1],
                        'sentence': sv
                    })

for w in words:
    if matches[w]:
        print(f"--- MATCH FOUND FOR: {w} ---")
        for m in matches[w]:
            print(f"  [{m['article']}] {m['sentence']}")
    else:
        print(f"NOT FOUND: {w}")

