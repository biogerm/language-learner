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
        
    with open(f, "r") as file:
        new_art = json.load(file)
        
    for s_old, s_new in zip(old_art.get("sentences", []), new_art.get("sentences", [])):
        for w_old, w_new in zip(s_old.get("target_words", []), s_new.get("target_words", [])):
            if not w_old.get("contextual_en") and w_new.get("contextual_en"):
                print(f"FOUND IT! Article: {f}")
                print(f"Sentence ID: {s_new.get('sentence_id')}")
                print(f"Word base_form: {w_new.get('base_form')}")
                print(f"New contextual_en added: {w_new.get('contextual_en')}")
