import json, glob

with open("output/missing_audio.json") as f:
    missing = json.load(f)

slash_words = set(missing["words"])
results = {w: [] for w in slash_words}

for filepath in glob.glob("../phase2/articles/article_*.json"):
    with open(filepath) as f:
        article = json.load(f)
        if not isinstance(article, dict):
            continue
        for sentence in article.get("sentences", []):
            for tw in sentence.get("target_words", []):
                bf = tw.get("base_form", "")
                if bf in slash_words:
                    results[bf].append({
                        "sentence_id": sentence["sentence_id"],
                        "word_in_sentence": tw.get("word_in_sentence", ""),
                        "sentence": sentence["sv"]
                    })

for w in slash_words:
    print(f"\n--- Base form: {w} ---")
    if not results[w]:
        print("  [Not used in any sentence]")
    for r in results[w]:
        print(f"  Used as: {r['word_in_sentence']}")
        print(f"  In sentence: {r['sentence']}")
