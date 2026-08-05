import json

def fix():
    with open("sfid_phase2_articles.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for step in data.get("steps", []):
        for article in step.get("articles", []):
            if article["article_id"] == "art_06":
                for sentence in article.get("sentences", []):
                    for target in sentence.get("target_words", []):
                        if target["base_form"] == "have":
                            target["base_form"] = "ha"
                            target["word_in_sentence"] = "har" # "Jag har en dröm"
            elif article["article_id"] == "art_44":
                for sentence in article.get("sentences", []):
                    for target in sentence.get("target_words", []):
                        if target["base_form"] == "freedom":
                            target["base_form"] = "frihet"
                            target["word_in_sentence"] = "frihet" # "modern frihet"
            elif article["article_id"] == "art_45":
                for sentence in article.get("sentences", []):
                    for target in sentence.get("target_words", []):
                        if target["base_form"] == "minded":
                            target["base_form"] = "öppensinnad"
                            target["word_in_sentence"] = "öppensinnad"
            elif article["article_id"] == "art_04":
                for sentence in article.get("sentences", []):
                    for target in sentence.get("target_words", []):
                        if target["base_form"] == "eyes,":
                            target["base_form"] = "blunda"
                            target["word_in_sentence"] = "blunda"
                            # I replaced '"Close your eyes," sa hon på engelska' with '"Blunda," sa hon'
            elif article["article_id"] == "art_12":
                for sentence in article.get("sentences", []):
                    for target in sentence.get("target_words", []):
                        if target["base_form"] == "ntally":
                            target["base_form"] = "mentalt"
                            target["word_in_sentence"] = "mentalt"

    # Recalculate indices for all
    for step in data.get("steps", []):
        for article in step.get("articles", []):
            for sentence in article.get("sentences", []):
                sv_text = sentence["sv"]
                for target in sentence.get("target_words", []):
                    word = target["word_in_sentence"]
                    idx = sv_text.lower().find(word.lower())
                    if idx != -1:
                        target["position_start"] = idx
                        target["position_end"] = idx + len(word)
                    else:
                        print(f"Article {article['article_id']}: WARNING: Cannot find '{word}' in sentence: {sv_text}")
                        
    with open("sfid_phase2_articles.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    import os
    for step in data.get("steps", []):
        for article in step.get("articles", []):
            art_id_str = article["article_id"]
            file_path = f"articles/article_{art_id_str.replace('art_','')}.json"
            if os.path.exists(file_path):
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(article, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    fix()
