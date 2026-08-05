import json

def main():
    with open("sfid_phase2_articles.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for step in data.get("steps", []):
        for article in step.get("articles", []):
            for sentence in article.get("sentences", []):
                for target in sentence.get("target_words", []):
                    if "ntally" in target["base_form"] or "ntally" in target["word_in_sentence"]:
                        print(f"Article {article['article_id']}: target contains ntally: {target}")

if __name__ == "__main__":
    main()
