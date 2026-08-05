import json

def main():
    with open("sfid_phase2_articles.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for step in data.get("steps", []):
        for article in step.get("articles", []):
            if article["article_id"] == "art_04":
                for sentence in article.get("sentences", []):
                    for target in sentence.get("target_words", []):
                        print(f"Target: {target['word_in_sentence']}")

if __name__ == "__main__":
    main()
