import json

def main():
    with open("sfid_phase2_articles.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for step in data.get("steps", []):
        for article in step.get("articles", []):
            for sentence in article.get("sentences", []):
                # Search the raw sv_text
                sv = sentence.get("sv", "").lower()
                for word in ['ntally', 'modern freedom', 'open-minded', 'i have a dream']:
                    if word in sv:
                        # Check if it's a target word
                        is_target = any(word in t["word_in_sentence"].lower() for t in sentence.get("target_words", []))
                        print(f"Article {article['article_id']}: '{word}' found in text. Is it a target? {is_target}")

if __name__ == "__main__":
    main()
