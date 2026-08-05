import json

def fix():
    with open("sfid_phase2_articles.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for step in data.get("steps", []):
        for article in step.get("articles", []):
            if article["article_id"] == "art_19":
                for sentence in article.get("sentences", []):
                    # "Det engelska ordet climate syns i varje taggmoln online." -> "Ordet klimat syns i varje taggmoln online."
                    if "engelska ordet climate" in sentence["sv"]:
                        sentence["sv"] = sentence["sv"].replace("Det engelska ordet climate", "Ordet klimat")
                    for target in sentence.get("target_words", []):
                        if target["word_in_sentence"] == "climate":
                            target["word_in_sentence"] = "klimat"
                            
            if article["article_id"] == "art_37":
                for sentence in article.get("sentences", []):
                    # "Filmen bygger på en bok av… en känd författare, på engelska kallad en book." -> "Filmen bygger på en känd bok av… en känd författare."
                    if "kallad en book" in sentence["sv"]:
                        sentence["sv"] = sentence["sv"].replace(", på engelska kallad en book", "")
                    for target in sentence.get("target_words", []):
                        if target["word_in_sentence"] == "book":
                            target["word_in_sentence"] = "bok"
                            
            if article["article_id"] == "art_04":
                for sentence in article.get("sentences", []):
                    # '"Close your eyes," sa hon på engelska när vi lyssnade på en lokal radiosändning om resor.'
                    # -> '"Blunda," sa hon när vi lyssnade på en lokal radiosändning om resor.'
                    if "Close your eyes" in sentence["sv"]:
                        sentence["sv"] = sentence["sv"].replace('"Close your eyes," sa hon på engelska', '"Blunda," sa hon')
                            
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
