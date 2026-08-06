import json

paths = ["course/sfid/phase2/articles_translated/art_19.json", "course/sfid/phase2/articles/article_19.json"]
for path in paths:
    with open(path, "r") as f:
        art = json.load(f)
    for s in art.get("sentences", []):
        tw_list = s.get("target_words", [])
        new_tw = [w for w in tw_list if w.get("base_form") not in ["Jag måste berätta en sak/en grej…", "Har du/ni hört att?"]]
        s["target_words"] = new_tw
    with open(path, "w", encoding="utf-8") as f:
        json.dump(art, f, ensure_ascii=False, indent=4)

print("Cleaned art_19.json")
