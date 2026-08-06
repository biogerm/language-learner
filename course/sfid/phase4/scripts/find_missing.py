import json, glob
for filepath in glob.glob("course/sfid/phase2/articles_translated/art_*.json"):
    if "art_19" in filepath: continue
    with open(filepath, "r") as f:
        art = json.load(f)
    for s in art.get("sentences", []):
        for w in s.get("target_words", []):
            if not w.get("contextual_en"):
                print(f"Article: {filepath}, Word: {w.get('base_form')}")
