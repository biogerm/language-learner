import json

with open("course/sfid/phase1/master_dictionary.json", "r") as f:
    master = json.load(f)
valid_words = set(master.get("words", {}).keys())

with open("course/sfid/phase2/articles_translated/art_19.json", "r") as f:
    art = json.load(f)

missing_targets = []
missing_secondary = []

for s in art.get("sentences", []):
    for tw in s.get("target_words", []):
        if tw.get("base_form") not in valid_words:
            missing_targets.append(tw.get("base_form"))
            
    for sw in s.get("secondary_words", []):
        if sw.get("base_form") not in valid_words:
            missing_secondary.append(sw.get("base_form"))

print(f"Missing target words in dict: {len(missing_targets)}")
if missing_targets:
    print(missing_targets)
    
print(f"Missing secondary words in dict: {len(missing_secondary)}")
if missing_secondary:
    print(list(set(missing_secondary)))
