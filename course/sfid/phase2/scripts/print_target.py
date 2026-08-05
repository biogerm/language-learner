import json

def main():
    with open("sfid_phase2_articles.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for step in data.get("steps", []):
        for article in step.get("articles", []):
            if article['article_id'] == 'art_06':
                for sentence in article.get("sentences", []):
                    for t in sentence.get("target_words", []):
                        if t["base_form"] == "have":
                            print(f"Text: {sentence['sv']}")
                            print(f"Target: {t}")
                            print(f"Extract: {sentence['sv'][t['position_start']:t['position_end']]}")
if __name__ == "__main__":
    main()
