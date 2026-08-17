import json, sqlite3

# 1. Load JSON
with open('course/sfid/phase1/master_dictionary.json', 'r', encoding='utf-8') as f:
    master_data = json.load(f)
    json_words = set(master_data['words'].keys())

# 2. Load DB
conn = sqlite3.connect('course/sfid/phase3/output/b1_vocab.db')
cursor = conn.cursor()
cursor.execute('SELECT word, en_translation FROM b1_vocabulary')
db_rows = cursor.fetchall()
db_words = set(row[0] for row in db_rows)
db_trans = {row[0]: row[1] for row in db_rows}
conn.close()

# 3. Check Word Count
print(f"JSON Total Words: {len(json_words)}")
print(f"DB Total Words: {len(db_words)}")

# 4. Check Set Differences
only_in_json = json_words - db_words
only_in_db = db_words - json_words

print(f"Words ONLY in JSON: {len(only_in_json)}")
for w in list(only_in_json)[:5]: print(f"  - {w}")
if len(only_in_json) > 5: print("  ...")

print(f"Words ONLY in DB: {len(only_in_db)}")
for w in list(only_in_db)[:5]: print(f"  - {w}")
if len(only_in_db) > 5: print("  ...")

# 5. Check Translation Consistency
mismatches = []
for w in json_words.intersection(db_words):
    json_t = master_data['words'][w].get('en', '').strip()
    db_t = db_trans[w].strip()
    if json_t != db_t:
        mismatches.append((w, json_t, db_t))

print(f"\nTranslation Mismatches: {len(mismatches)}")
for w, j, d in mismatches[:10]:
    print(f"  [{w}] JSON: '{j}' | DB: '{d}'")

