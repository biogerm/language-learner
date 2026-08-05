import json

def fix():
    with open("sfid_phase2_articles.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for step in data.get("steps", []):
        for article in step.get("articles", []):
            if article["article_id"] == "art_38":
                for sentence in article.get("sentences", []):
                    sv_text = sentence["sv"]
                    for target in sentence.get("target_words", []):
                        word = target["word_in_sentence"]
                        
                        if word == "förvånansvärd" and "förvånansvärt" in sv_text:
                            target["word_in_sentence"] = "förvånansvärt"
                            
                        elif word == "fritidsvana" and "fritid" in sv_text:
                            target["word_in_sentence"] = "fritid"
                            
                        elif word == "jordig" and "jord" in sv_text:
                            target["word_in_sentence"] = "jord"
                            
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
                        print(f"WARNING STILL: Cannot find '{word}' in sentence: {sv_text}")
                        
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
