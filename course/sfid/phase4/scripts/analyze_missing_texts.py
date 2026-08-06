import json, os

with open("output/missing_audio.json") as f:
    missing = json.load(f)

# Words
print("--- MISSING WORDS ---")
for w in missing["words"]:
    print(w)

# Sentences
import glob
target_texts = {}
for filepath in glob.glob("../phase2/articles/article_*.json"):
    with open(filepath) as f:
        article = json.load(f)
        if isinstance(article, dict):
            for item in article.get("sentences", []):
                target_texts[item["sentence_id"]] = item["sv"]

print("\n--- SENTENCE CAUSE ANALYSIS ---")
quotes = 0
others = []
for s_id in missing["sentences"]:
    text = target_texts.get(s_id, "")
    if '"' in text:
        quotes += 1
    else:
        others.append((s_id, text))

print(f"Sentences with double quotes: {quotes}")
print(f"Sentences with OTHER issues: {len(others)}")
for s_id, text in others[:10]:
    print(f"- {s_id}: {text}")
