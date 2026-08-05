import json
import glob

def main():
    with open("generated_titles.json", "r", encoding="utf-8") as f:
        titles = json.load(f)
        
    for d in ["articles", "articles_translated"]:
        files = glob.glob(f"{d}/art_*.json") + glob.glob(f"{d}/article_*.json")
        for filepath in files:
            if "article_plan.json" in filepath: continue
            
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            art_id = data.get("article_id")
            if art_id in titles:
                data["article_title"] = titles[art_id]
                
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                    
    print("New titles injected into both folders successfully.")

if __name__ == "__main__":
    main()
