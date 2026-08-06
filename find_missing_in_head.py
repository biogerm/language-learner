import json, subprocess, glob
files = glob.glob("course/sfid/phase2/articles_translated/art_*.json")
for f in files:
    if "art_19" in f: continue
    if "art_57" in f: continue
    try:
        old_content = subprocess.check_output(["git", "show", f"HEAD:{f}"], text=True, stderr=subprocess.DEVNULL)
        old_art = json.loads(old_content)
    except Exception: continue
    for s in old_art.get("sentences", []):
        for w in s.get("target_words", []):
            if not w.get("contextual_en"):
                print(f"FOUND IN HEAD: {f}, word: {w.get('base_form')}")
