import json
import sqlite3
import glob
import os

os.makedirs("../phase3/output", exist_ok=True)
db_path = "../phase3/output/b1_vocab.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS b1_vocabulary (
        word TEXT PRIMARY KEY,
        en_translation TEXT NOT NULL,
        sv_context TEXT NOT NULL,
        source TEXT NOT NULL
    )
''')

with open("../phase1/master_dictionary.json", "r", encoding="utf-8") as f:
    master_data = json.load(f)["words"]

files = sorted(glob.glob("../phase2/articles_translated/art_*.json"))
extracted_contexts = {}

for filepath in files:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    article_title = data.get("article_title", "Unknown Title")
    primary_words = set(data.get("primary_words_used", []))
    
    for s in data["sentences"]:
        sv_sentence = s["sv"]
        for tw in s.get("target_words", []):
            base_form = tw["base_form"]
            
            if base_form in primary_words and base_form in master_data:
                # Store the extracted context, later occurrences will overwrite earlier ones in same article
                extracted_contexts[base_form] = {
                    "sv_context": sv_sentence,
                    "source": article_title
                }

records_to_insert = []
missing_count = 0

for base_form, properties in master_data.items():
    en_trans = properties.get("en", "")
    
    if base_form in extracted_contexts:
        ctx = extracted_contexts[base_form]
        sv_context = ctx["sv_context"]
        source = ctx["source"]
    else:
        # Fallback for the 111 missing words to satisfy DB schema
        sv_context = "Exempel saknas i nuvarande korpus."
        source = "System"
        missing_count += 1
        
    records_to_insert.append((base_form, en_trans, sv_context, source))

upsert_query = '''
    INSERT INTO b1_vocabulary (word, en_translation, sv_context, source)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(word) DO UPDATE SET
        en_translation=excluded.en_translation,
        sv_context=excluded.sv_context,
        source=excluded.source;
'''

cursor.executemany(upsert_query, records_to_insert)
conn.commit()

cursor.execute("SELECT COUNT(*) FROM b1_vocabulary")
count = cursor.fetchone()[0]

print(f"Successfully processed and inserted {count} words into the database.")
print(f"Number of words that used fallback context (due to missing extraction/generation): {missing_count}")

conn.close()
