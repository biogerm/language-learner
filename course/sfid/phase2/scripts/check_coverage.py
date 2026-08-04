import json

with open("sfid_phase2_articles_v2.json", "r", encoding="utf-8") as f:
    data = json.load(f)

with open("../phase1/master_dictionary.json", "r", encoding="utf-8") as f:
    master_dict = json.load(f)
    
total_dict_words = sum(len(theme_data["words"]) for theme_data in master_dict.values())

used_lines = set()

for step in data.get("steps", []):
    for article in step.get("articles", []):
        for sentence in article.get("sentences", []):
            for target in sentence.get("target_words", []):
                used_lines.add(target.get("source_line"))

print(f"Total dictionary words: {total_dict_words}")
print(f"Total unique words used in Phase 2 articles: {len(used_lines)}")
