import json
import glob
import os

def main():
    original_files = sorted(glob.glob("articles/article_*.json"))
    
    for orig_file in original_files:
        # Get the ID, e.g., article_00.json -> art_00.json
        basename = os.path.basename(orig_file)
        if basename == "article_plan.json":
            continue
            
        idx = basename.replace("article_", "").replace(".json", "")
        trans_file = f"articles_translated/art_{idx}.json"
        
        if not os.path.exists(trans_file):
            print(f"Missing translated file: {trans_file}")
            continue
            
        with open(orig_file, "r", encoding="utf-8") as f:
            orig_data = json.load(f)
            
        with open(trans_file, "r", encoding="utf-8") as f:
            trans_data = json.load(f)
            
        # Create a dictionary of translated sentences
        trans_sentences = {}
        for s in trans_data.get("sentences", []):
            trans_sentences[s["sentence_id"]] = {
                "en": s.get("en", ""),
                "target_words": s.get("target_words", [])
            }
            
        # Inject translations and fixed target_words into original data
        for s in orig_data.get("sentences", []):
            sid = s["sentence_id"]
            if sid in trans_sentences:
                s["en"] = trans_sentences[sid]["en"]
                s["target_words"] = trans_sentences[sid]["target_words"]
                
        # Write back to the original file
        with open(orig_file, "w", encoding="utf-8") as f:
            json.dump(orig_data, f, ensure_ascii=False, indent=4)
            
    print("Injected translations into git-tracked files successfully.")

if __name__ == "__main__":
    main()
