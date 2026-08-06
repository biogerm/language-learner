import json

with open("../phase1/master_dictionary.json", "r", encoding="utf-8") as f:
    master_data = json.load(f)["words"]

import glob

files = sorted(glob.glob("../phase2/articles_translated/art_*.json"))
words_found = set()

for filepath in files:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    primary_words = set(data.get("primary_words_used", []))
    for s in data["sentences"]:
        for tw in s.get("target_words", []):
            bf = tw["base_form"]
            if bf in primary_words:
                words_found.add(bf)

missing = set(master_data.keys()) - words_found
print(f"Missing words count: {len(missing)}")
print("First 20 missing words:")
print(list(missing)[:20])
