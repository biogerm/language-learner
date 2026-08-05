import json

def main():
    with open("sfid_phase2_articles.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for step in data.get("steps", []):
        for article in step.get("articles", []):
            for sentence in article.get("sentences", []):
                for target in sentence.get("target_words", []):
                    base = target["base_form"].lower()
                    if base in ["modern freedom", "open-minded", "i have a dream", "book", "climate"]:
                        print(f"Article {article['article_id']}: target contains english base form: {target}")

if __name__ == "__main__":
    main()
