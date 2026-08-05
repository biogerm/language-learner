import json
import os

def main():
    # 1. Read the main file
    with open("sfid_phase2_articles.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    course_id = data.get("course_id", "sfid")
    course_title = data.get("course_title", "SFI D")
    
    # Rename steps to stages in the master data
    if "steps" in data:
        data["stages"] = data.pop("steps")
        
    for stage in data.get("stages", []):
        # Rename step_id to stage_id
        if "step_id" in stage:
            stage["stage_id"] = stage.pop("step_id")
        # Rename step_title to stage_title
        if "step_title" in stage:
            stage["stage_title"] = stage.pop("step_title")
            
        stage_id = stage.get("stage_id")
        stage_title = stage.get("stage_title")
        
        # Now process each article
        for article in stage.get("articles", []):
            art_id_str = article["article_id"]
            
            # We want to output to articles/article_{id}.json
            # And inject the hierarchical information
            out_obj = {
                "course_id": course_id,
                "course_title": course_title,
                "stage_id": stage_id,
                "stage_title": stage_title
            }
            # Add all existing article keys
            for k, v in article.items():
                out_obj[k] = v
                
            file_name = f"articles/article_{art_id_str.replace('art_','')}.json"
            if os.path.exists("articles"):
                with open(file_name, "w", encoding="utf-8") as f:
                    json.dump(out_obj, f, ensure_ascii=False, indent=2)
                    
    # Save the updated master file
    with open("sfid_phase2_articles.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
