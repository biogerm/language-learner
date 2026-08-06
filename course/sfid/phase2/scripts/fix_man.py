import json
with open("articles_translated/art_05.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for s in data["sentences"]:
    if s["sentence_id"] == "art_05_s001":
        for tw in s["target_words"]:
            if tw["word_in_sentence"] == "man":
                tw["contextual_en"] = "one (generic pronoun)"
                
with open("articles_translated/art_05.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
