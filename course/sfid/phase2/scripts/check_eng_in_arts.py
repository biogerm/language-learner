import json

def main():
    with open("sfid_phase2_articles.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for step in data.get("steps", []):
        for article in step.get("articles", []):
            if article["article_id"] in ["art_06", "art_12", "art_44", "art_45"]:
                for sentence in article.get("sentences", []):
                    print(f"{article['article_id']}: {sentence['sv']}")

if __name__ == "__main__":
    main()
