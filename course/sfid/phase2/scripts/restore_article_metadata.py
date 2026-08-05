import json
import glob
import os

def main():
    original_files = glob.glob("articles/article_*.json")
    
    restored_count = 0
    for orig_file in original_files:
        # Extract article index, e.g., article_05.json -> 05
        basename = os.path.basename(orig_file)
        idx = basename.replace("article_", "").replace(".json", "")
        
        translated_file = f"articles_translated/art_{idx}.json"
        
        if not os.path.exists(translated_file):
            print(f"Warning: Translated file not found: {translated_file}")
            continue
            
        with open(orig_file, "r", encoding="utf-8") as f:
            orig_data = json.load(f)
            
        with open(translated_file, "r", encoding="utf-8") as f:
            trans_data = json.load(f)
            
        # Restore metadata
        trans_data["course_id"] = orig_data.get("course_id", "sfid")
        trans_data["course_title"] = orig_data.get("course_title", "SFI D")
        trans_data["stage_id"] = orig_data.get("stage_id", "")
        trans_data["stage_title"] = orig_data.get("stage_title", "")
        trans_data["article_title"] = orig_data.get("article_title", "")
        
        # We need to reorder the dictionary so metadata is at the top
        ordered_data = {
            "course_id": trans_data["course_id"],
            "course_title": trans_data["course_title"],
            "stage_id": trans_data["stage_id"],
            "stage_title": trans_data["stage_title"],
            "article_id": trans_data["article_id"],
            "article_title": trans_data["article_title"],
            "target_word_count": trans_data.get("target_word_count", 0)
        }
        
        # Add remaining keys
        for k, v in trans_data.items():
            if k not in ordered_data and k != "stage": # remove the bad "stage" key we added earlier
                ordered_data[k] = v
                
        with open(translated_file, "w", encoding="utf-8") as f:
            json.dump(ordered_data, f, ensure_ascii=False, indent=4)
            
        restored_count += 1
        
    print(f"Successfully restored metadata for {restored_count} articles.")

if __name__ == "__main__":
    main()
