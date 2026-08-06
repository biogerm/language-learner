import json, glob

with open("course/sfid/phase1/master_dictionary.json", "r") as f:
    master = json.load(f)
valid_words = set(master.get("words", {}).keys())

missing = 0
total = 0
for filepath in glob.glob("course/sfid/phase2/articles_translated/art_*.json"):
    with open(filepath, "r") as f:
        art = json.load(f)
    for s in art.get("sentences", []):
        for sw in s.get("secondary_words", []):
            total += 1
            if sw.get("base_form") not in valid_words:
                missing += 1

print(f"Total secondary words across all articles: {total}")
print(f"Secondary words NOT in master dictionary: {missing}")
