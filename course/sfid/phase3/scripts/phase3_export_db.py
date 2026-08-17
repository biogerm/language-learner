import json
import sqlite3
import glob
import os

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # sfid
    db_path = os.path.join(base_dir, "phase3", "output", "b1_vocab.db")
    
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS b1_vocabulary (
            word TEXT PRIMARY KEY,
            word_type TEXT,
            noun_gender TEXT,
            is_regular_verb BOOLEAN,
            verb_imperativ TEXT,
            verb_presens TEXT,
            verb_preteritum TEXT,
            verb_supinum TEXT,
            verb_perfekt_particip TEXT,
            adj_en TEXT,
            adj_ett TEXT,
            adj_plural TEXT,
            adj_komparativ TEXT,
            adj_superlativ TEXT,
            en_translation TEXT NOT NULL,
            sv_context TEXT NOT NULL,
            sentence_audio_filename TEXT,
            source TEXT NOT NULL
        )
    ''')

    dict_path = os.path.join(base_dir, "phase1", "master_dictionary.json")
    with open(dict_path, "r", encoding="utf-8") as f:
        master_data = json.load(f)["words"]

    meta_path = os.path.join(base_dir, "phase3", "data", "word_metadata.json")
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            metadata_cache = json.load(f)
    else:
        metadata_cache = {}

    articles_pattern = os.path.join(base_dir, "phase2", "articles", "article_*.json")
    files = sorted(glob.glob(articles_pattern))
    files = [f for f in files if not f.endswith("article_plan.json")]
    
    if not files:
        # fallback if not in articles
        articles_pattern = os.path.join(base_dir, "phase2", "articles_translated", "art_*.json")
        files = sorted(glob.glob(articles_pattern))

    extracted_contexts = {}

    for filepath in files:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        article_title = data.get("article_title", "Unknown Title")
        primary_words = set(data.get("primary_words_used", []))
        
        for s in data.get("sentences", []):
            sv_sentence = s.get("sv", "")
            sent_id = s.get("sentence_id", "")
            # Example art_01_s001 -> art01_s001.mp3
            # Or if it's already like art01_s001, just add .mp3
            audio_filename = sent_id.replace("_", "", 1) + ".mp3" if sent_id.startswith("art_") else sent_id + ".mp3"
            if not sent_id:
                audio_filename = None

            for tw in s.get("target_words", []):
                base_form = tw.get("base_form", "")
                
                # Check if it's a primary target word
                if base_form in primary_words and base_form in master_data:
                    # Store the extracted context, later occurrences will overwrite earlier ones in same article
                    extracted_contexts[base_form] = {
                        "sv_context": sv_sentence,
                        "source": article_title,
                        "audio": audio_filename
                    }

    records_to_insert = []
    missing_count = 0

    for base_form, properties in master_data.items():
        en_trans = properties.get("en", "")
        
        meta = metadata_cache.get(base_form, {})
        word_type = meta.get("word_type")
        noun_gender = meta.get("noun_gender")
        is_regular = meta.get("is_regular_verb")
        v_imp = meta.get("verb_imperativ")
        v_pres = meta.get("verb_presens")
        v_pret = meta.get("verb_preteritum")
        v_sup = meta.get("verb_supinum")
        v_perf = meta.get("verb_perfekt_particip")
        
        adj_en = meta.get("adj_en")
        adj_ett = meta.get("adj_ett")
        adj_plural = meta.get("adj_plural")
        adj_kom = meta.get("adj_komparativ")
        adj_sup = meta.get("adj_superlativ")
        
        if base_form in extracted_contexts:
            ctx = extracted_contexts[base_form]
            sv_context = ctx["sv_context"]
            source = ctx["source"]
            audio = ctx.get("audio")
        else:
            # Fallback for missing words
            sv_context = "Exempel saknas i nuvarande korpus."
            source = "System"
            audio = None
            missing_count += 1
            
        records_to_insert.append((
            base_form, word_type, noun_gender, is_regular,
            v_imp, v_pres, v_pret, v_sup, v_perf,
            adj_en, adj_ett, adj_plural, adj_kom, adj_sup,
            en_trans, sv_context, audio, source
        ))

    upsert_query = '''
        INSERT INTO b1_vocabulary (
            word, word_type, noun_gender, is_regular_verb, verb_imperativ, verb_presens, 
            verb_preteritum, verb_supinum, verb_perfekt_particip, 
            adj_en, adj_ett, adj_plural, adj_komparativ, adj_superlativ,
            en_translation, sv_context, sentence_audio_filename, source
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(word) DO UPDATE SET
            word_type=excluded.word_type,
            noun_gender=excluded.noun_gender,
            is_regular_verb=excluded.is_regular_verb,
            verb_imperativ=excluded.verb_imperativ,
            verb_presens=excluded.verb_presens,
            verb_preteritum=excluded.verb_preteritum,
            verb_supinum=excluded.verb_supinum,
            verb_perfekt_particip=excluded.verb_perfekt_particip,
            adj_en=excluded.adj_en,
            adj_ett=excluded.adj_ett,
            adj_plural=excluded.adj_plural,
            adj_komparativ=excluded.adj_komparativ,
            adj_superlativ=excluded.adj_superlativ,
            en_translation=excluded.en_translation,
            sv_context=excluded.sv_context,
            sentence_audio_filename=excluded.sentence_audio_filename,
            source=excluded.source;
    '''

    cursor.executemany(upsert_query, records_to_insert)
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM b1_vocabulary")
    count = cursor.fetchone()[0]

    print(f"Successfully processed and inserted {count} words into the database.")
    print(f"Number of words that used fallback context: {missing_count}")

    conn.close()

if __name__ == '__main__':
    main()
