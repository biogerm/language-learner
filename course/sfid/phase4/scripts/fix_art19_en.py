import json, glob, os

# Load master dictionary for English translations
with open("course/sfid/phase1/master_dictionary.json", "r") as f:
    master = json.load(f)
dict_words = master.get("words", {})

translated_dir = "course/sfid/phase2/articles_translated"
untranslated_dir = "course/sfid/phase2/articles"

fixed_count = 0

for filepath in glob.glob(os.path.join(translated_dir, "art_*.json")):
    with open(filepath, "r") as f:
        art = json.load(f)
        
    modified = False
    for s in art.get("sentences", []):
        for w in s.get("target_words", []):
            if not w.get("contextual_en"):
                base_form = w.get("base_form")
                if base_form in dict_words:
                    w["contextual_en"] = dict_words[base_form].get("en", "")
                    modified = True
                    fixed_count += 1
                    
    if modified:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(art, f, ensure_ascii=False, indent=4)
            
        # Also sync back to untranslated article just in case (though untranslated should NOT have contextual_en)
        # But we'll just write it and let it be structurally sound.
        untrans = json.loads(json.dumps(art))
        untrans["article_id"] = untrans["article_id"].replace("art_", "article_")
        for s in untrans.get("sentences", []):
            s["en"] = ""
            for tw in s.get("target_words", []):
                tw.pop("contextual_en", None)
            for sw in s.get("secondary_words", []):
                sw.pop("contextual_en", None)
                
        untrans_file = os.path.join(untranslated_dir, os.path.basename(filepath).replace("art_", "article_"))
        with open(untrans_file, "w", encoding="utf-8") as f:
            json.dump(untrans, f, ensure_ascii=False, indent=4)

print(f"Fixed missing contextual_en for {fixed_count} target words across articles.")
