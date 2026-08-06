import json
import glob

with open("../phase1/master_dictionary.json", "r", encoding="utf-8") as f:
    master_data = json.load(f)["words"]

files = sorted(glob.glob("../phase2/articles_translated/art_*.json"))
words_found = set()
article_word_map = {}

for filepath in files:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    art_id = filepath.split('/')[-1]
    primary_words = set(data.get("primary_words_used", []))
    article_word_map[art_id] = primary_words
    
    for s in data["sentences"]:
        for tw in s.get("target_words", []):
            bf = tw["base_form"]
            if bf in primary_words:
                words_found.add(bf)

missing = set(master_data.keys()) - words_found

# Find which articles contain these missing words in their primary_words_used array
missing_per_art = {}
for mw in missing:
    found_in = []
    for art, pw in article_word_map.items():
        if mw in pw:
            found_in.append(art)
    for art in found_in:
        missing_per_art[art] = missing_per_art.get(art, 0) + 1

for art, count in sorted(missing_per_art.items()):
    print(f"{art}: {count} missing words")
