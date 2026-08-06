import json, glob, subprocess

files = glob.glob("course/sfid/phase2/articles_translated/art_*.json")
for f in files:
    if "art_19" in f: continue
    if "art_57" in f: continue
    
    try:
        old_content = subprocess.check_output(["git", "show", f"HEAD:{f}"], text=True, stderr=subprocess.DEVNULL)
        old_art = json.loads(old_content)
    except Exception:
        continue
        
    old_missing = []
    for s in old_art.get("sentences", []):
        for w in s.get("target_words", []):
            if not w.get("contextual_en"):
                old_missing.append(w.get("base_form"))
                
    with open(f, "r") as file:
        new_art = json.load(file)
        
    new_missing = []
    for s in new_art.get("sentences", []):
        for w in s.get("target_words", []):
            if not w.get("contextual_en"):
                new_missing.append(w.get("base_form"))
                
    for word in old_missing:
        if word not in new_missing:
            print(f"FOUND IT! Article: {f}, Word: {word}")
