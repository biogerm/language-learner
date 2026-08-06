import json

with open("invalid_mappings.json", "r", encoding="utf-8") as f:
    invalid_list = json.load(f)

# Create a set for O(1) lookup
invalid_set = set(invalid_list)

# Load master dictionary
with open("../phase1/master_dictionary.json", "r", encoding="utf-8") as f:
    master = json.load(f)["words"]

import glob

files = glob.glob("articles_translated/art_*.json")
fixed_count = 0

for filepath in files:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    modified = False
    for s in data["sentences"]:
        sid = s["sentence_id"]
        for tw in s.get("target_words", []):
            bf = tw["base_form"]
            key = f"{sid}:::{bf}"
            if key in invalid_set:
                if bf in master:
                    master_en = master[bf].get("en", "")
                    tw["contextual_en"] = master_en
                    modified = True
                    fixed_count += 1
                    
    if modified:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

print(f"Fixed {fixed_count} invalid mappings by reverting them to master_en.")
