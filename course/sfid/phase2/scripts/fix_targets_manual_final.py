import json

def fix():
    with open("sfid_phase2_articles.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for step in data.get("steps", []):
        for article in step.get("articles", []):
            if article["article_id"] == "art_36":
                for sentence in article.get("sentences", []):
                    # Revert 'spela död' -> 'leka skådespelare'
                    if "spela död" in sentence["sv"]:
                        sentence["sv"] = sentence["sv"].replace("spela död", "leka skådespelare")
                    for target in sentence.get("target_words", []):
                        if target["word_in_sentence"] == "spela död":
                            target["word_in_sentence"] = "skådespelare"
                            
            if article["article_id"] == "art_37":
                for sentence in article.get("sentences", []):
                    # Revert the removal of ' på engelska kallad en book'
                    # The text was: 'Filmen bygger på en bok av... en känd författare,. Filmen bygger på en verklig händelse.'
                    if "en bok av… en känd författare,." in sentence["sv"]:
                        sentence["sv"] = sentence["sv"].replace("en bok av… en känd författare,.", "en bok av… en känd författare, på engelska kallad en book.")
                    for target in sentence.get("target_words", []):
                        if target["word_in_sentence"] == "smart mobil":
                            target["word_in_sentence"] = "smarta mobil"
                            
            if article["article_id"] == "art_38":
                for sentence in article.get("sentences", []):
                    for target in sentence.get("target_words", []):
                        if target["word_in_sentence"] == "golfspelare":
                            target["word_in_sentence"] = "golfspelarna"
                            
    # Recalculate again
    for step in data.get("steps", []):
        for article in step.get("articles", []):
            for sentence in article.get("sentences", []):
                sv_text = sentence["sv"]
                for target in sentence.get("target_words", []):
                    word = target["word_in_sentence"]
                    idx = sv_text.find(word)
                    if idx != -1:
                        target["position_start"] = idx
                        target["position_end"] = idx + len(word)
                    else:
                        print(f"Article {article['article_id']}: WARNING STILL: Cannot find '{word}' in sentence: {sv_text}")
                        
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
