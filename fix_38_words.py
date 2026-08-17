import sqlite3, json, glob, re

# The 5 missing words
truly_missing = ['så lång tid', 'kombinera', 'climate', 'realisation', 'form av']

# 1. Update the JSON
json_path = 'course/sfid/phase1/master_dictionary.json'
with open(json_path, 'r', encoding='utf-8') as f:
    master_data = json.load(f)

for w in truly_missing:
    if w in master_data['words']:
        del master_data['words'][w]

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(master_data, f, indent=4, ensure_ascii=False)

# 2. Get the 33 words to rescue
conn = sqlite3.connect('course/sfid/phase3/output/b1_vocab.db')
cursor = conn.cursor()
cursor.execute("SELECT word FROM b1_vocabulary WHERE source='System'")
fallback_words = [row[0] for row in cursor.fetchall()]
words_to_rescue = [w for w in fallback_words if w not in truly_missing]

# 3. Find 1 sentence/audio for each word_to_rescue
patterns = {w: re.compile(r'\b' + re.escape(w.lower()).replace('…', '.*') + r'\b', re.IGNORECASE) for w in words_to_rescue}
articles = glob.glob('course/sfid/phase2/articles_translated/art_*.json')

rescued_data = {}
for a_path in articles:
    with open(a_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for s in data.get('sentences', []):
            sv = s.get('sv', '')
            for w in words_to_rescue:
                if w not in rescued_data and patterns[w].search(sv):
                    rescued_data[w] = {
                        'sv_context': sv,
                        'source': data.get('title', 'Unknown'),
                        'audio': s.get('audio_filename')
                    }

# 4. Update the DB
for w, d in rescued_data.items():
    cursor.execute('''
        UPDATE b1_vocabulary 
        SET sv_context = ?, source = ?, sentence_audio_filename = ?
        WHERE word = ?
    ''', (d['sv_context'], d['source'], d['audio'], w))

# 5. Delete the 5 words from DB
for w in truly_missing:
    cursor.execute('DELETE FROM b1_vocabulary WHERE word = ?', (w,))

conn.commit()
conn.close()

print(f"Rescued {len(rescued_data)} words in DB.")
print(f"Deleted {len(truly_missing)} words from JSON and DB.")
