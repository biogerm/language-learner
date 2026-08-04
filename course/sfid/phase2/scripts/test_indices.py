import json

with open("article_0.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    sv = data["sv"]
    for tw in data["target_words"]:
        start = tw["position_start"]
        end = tw["position_end"]
        extracted = sv[start:end]
        if extracted != tw["word_in_sentence"]:
            print(f"ERROR: {tw['word_in_sentence']} != {extracted} (at {start}:{end})")
        else:
            print(f"OK: {extracted}")
