import json
import glob
import string
import re

def normalize(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'\(.*?\)', '', text) # remove text in parenthesis
    text = ''.join(ch for ch in text if ch not in string.punctuation)
    return text.strip()

with open("../phase1/master_dictionary.json", "r", encoding="utf-8") as f:
    master = json.load(f)["words"]

discrepancies = {}

files = glob.glob("articles_translated/art_*.json")
for filepath in files:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    for s in data["sentences"]:
        sid = s["sentence_id"]
        for tw in s.get("target_words", []):
            bf = tw["base_form"]
            ctx_en = tw.get("contextual_en", "")
            
            if bf in master:
                master_en = master[bf].get("en", "")
                
                n_ctx = normalize(ctx_en)
                n_mas = normalize(master_en)
                
                # Check if one is a substring of another or identical
                if n_ctx == n_mas or n_ctx in n_mas or n_mas in n_ctx:
                    continue
                else:
                    # Collect discrepancy
                    if sid not in discrepancies:
                        discrepancies[sid] = {
                            "sv_sentence": s["sv"],
                            "en_sentence": s["en"],
                            "words": []
                        }
                    discrepancies[sid]["words"].append({
                        "base_form": bf,
                        "word_in_sentence": tw["word_in_sentence"],
                        "contextual_en": ctx_en,
                        "master_en": master_en
                    })

with open("discrepancies.json", "w", encoding="utf-8") as f:
    json.dump(discrepancies, f, ensure_ascii=False, indent=4)
    
count = sum(len(d["words"]) for d in discrepancies.values())
print(f"Found {count} discrepancies across {len(discrepancies)} sentences.")
