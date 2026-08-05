import json
import os

def main():
    with open("sfid_phase2_articles.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for stage in data.get("stages", []):
        old_id = stage.get("stage_id", "")
        if old_id.startswith("step_"):
            stage["stage_id"] = old_id.replace("step_", "stage_")
            
        stage_id = stage["stage_id"]
        
        for article in stage.get("articles", []):
            art_id_str = article["article_id"]
            file_name = f"articles/article_{art_id_str.replace('art_','')}.json"
            if os.path.exists(file_name):
                with open(file_name, "r", encoding="utf-8") as f:
                    art_data = json.load(f)
                art_data["stage_id"] = stage_id
                with open(file_name, "w", encoding="utf-8") as f:
                    json.dump(art_data, f, ensure_ascii=False, indent=2)

    with open("sfid_phase2_articles.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
