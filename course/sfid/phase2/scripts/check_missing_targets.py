import json
with open("sfid_phase2_articles.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for step in data.get("steps", []):
    for article in step.get("articles", []):
        for sentence in article.get("sentences", []):
            sv_text = sentence["sv"]
            for target in sentence.get("target_words", []):
                word = target["word_in_sentence"]
                idx = sv_text.find(word)
                if idx == -1:
                    print(f"Article {article['article_id']}: Missing '{word}' in '{sv_text}'")
