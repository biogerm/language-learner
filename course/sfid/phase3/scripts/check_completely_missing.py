import json
import glob

with open("../phase1/master_dictionary.json", "r", encoding="utf-8") as f:
    master_data = json.load(f)["words"]

files = sorted(glob.glob("../phase2/articles_translated/art_*.json"))
all_primary_words = set()

for filepath in files:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    primary_words = set(data.get("primary_words_used", []))
    all_primary_words.update(primary_words)

never_used = set(master_data.keys()) - all_primary_words
print(f"Words completely missing from ANY primary_words_used array: {len(never_used)}")
print(list(never_used)[:20])
