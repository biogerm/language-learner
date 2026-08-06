import json, glob

with open("../phase1/master_dictionary.json") as f:
    master = json.load(f)
master_words = set(master.get("words", {}).keys())

used_words = set()
slash_sentences = []

for filepath in glob.glob("../phase2/articles/article_*.json"):
    with open(filepath) as f:
        article = json.load(f)
        if not isinstance(article, dict):
            continue
        
        sentences = article.get("sentences", [])
        for i, s in enumerate(sentences):
            # Check for words used
            for tw in s.get("target_words", []):
                used_words.add(tw.get("base_form", ""))
            
            # Check for slashes in the sentence text itself
            sv_text = s["sv"]
            if "/" in sv_text:
                prev_s = sentences[i-1]["sv"] if i > 0 else "(Start of article)"
                next_s = sentences[i+1]["sv"] if i < len(sentences)-1 else "(End of article)"
                slash_sentences.append({
                    "id": s["sentence_id"],
                    "text": sv_text,
                    "prev": prev_s,
                    "next": next_s
                })

print("=== Slashes in Sentences ===")
for item in slash_sentences:
    print(f"[{item['id']}]")
    print(f"Prev: {item['prev']}")
    print(f"Orig: {item['text']}")
    print(f"Next: {item['next']}")
    print()

unused_words = master_words - used_words
print(f"=== Unused Words ({len(unused_words)} total) ===")
for w in sorted(unused_words):
    print(f"- {w}")

