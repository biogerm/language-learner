import json
import glob
import os

def main():
    archive_file = "archive/sfid_phase2_articles_translated.json"
    if not os.path.exists(archive_file):
        print("Archive missing!")
        return
        
    with open(archive_file, "r", encoding="utf-8") as f:
        arch_data = json.load(f)
        
    # Build a dictionary of translations from the monolithic json
    trans_dict = {}
    for stage in arch_data.get("stages", []):
        for art in stage.get("articles", []):
            for s in art.get("sentences", []):
                # normalize ID for lookup
                sid_norm = s["sentence_id"].replace("art", "art_").replace("art__", "art_")
                trans_dict[sid_norm] = {
                    "en": s.get("en", ""),
                    "target_words": s.get("target_words", [])
                }
                
    # Inject into articles_translated/
    files = glob.glob("articles_translated/art_*.json")
    for filepath in files:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        modified = False
        for s in data.get("sentences", []):
            sid = s["sentence_id"]
            sid_norm = sid.replace("art", "art_").replace("art__", "art_")
            if sid_norm in trans_dict:
                s["en"] = trans_dict[sid_norm]["en"]
                s["target_words"] = trans_dict[sid_norm]["target_words"]
                modified = True
                
        if modified:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                
    print("Translations injected into articles_translated.")

if __name__ == "__main__":
    main()
