import json
import os

def main():
    input_file = "sfid_phase2_articles_translated.json"
    output_dir = "articles_translated"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    count = 0
    # Process each stage and its articles
    for stage in data.get("stages", []):
        stage_name = stage.get("stage", "unknown_stage")
        for article in stage.get("articles", []):
            article_id = article.get("article_id")
            if not article_id:
                continue
                
            # Add stage info to the article dict so it's not lost
            article["stage"] = stage_name
            
            output_file = os.path.join(output_dir, f"{article_id}.json")
            with open(output_file, "w", encoding="utf-8") as out_f:
                json.dump(article, out_f, ensure_ascii=False, indent=4)
            count += 1
            
    print(f"Successfully split {count} articles into {output_dir}/")

if __name__ == "__main__":
    main()
