import json
import re

def main():
    with open("sfid_phase2_articles.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for step in data.get("steps", []):
        for article in step.get("articles", []):
            for sentence in article.get("sentences", []):
                for target in sentence.get("target_words", []):
                    # Check for some known english target words from previous steps
                    word = target["word_in_sentence"].lower()
                    if word in ['book', 'climate', 'modern freedom', 'open-minded', 'i have a dream', 'ntally']:
                        print(f"Article {article['article_id']}: Target word found: {word}")

if __name__ == "__main__":
    main()
