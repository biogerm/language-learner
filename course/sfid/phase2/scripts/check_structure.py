import json

def main():
    with open("sfid_phase2_articles.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    print(f"Top level keys: {list(data.keys())}")
    for i, step in enumerate(data.get("steps", [])):
        print(f"Step {i}: {step.get('step_id')}, Articles count: {len(step.get('articles', []))}")
        for j, article in enumerate(step.get("articles", [])):
            if j == 0 or article['article_id'] in ['art_09', 'art_10', 'art_11']:
                print(f"  Article {article['article_id']}: keys={list(article.keys())}")

if __name__ == "__main__":
    main()
