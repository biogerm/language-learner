import json

with open("sfid_phase2_articles_v2.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for step in data.get("steps", []):
    for article in step.get("articles", []):
        for sentence in article.get("sentences", []):
            sv_text = sentence["sv"]
            for target in sentence.get("target_words", []):
                # Fix 'knäppt' -> 'knäpp' in article 14
                if target["word_in_sentence"] == "knäppt" and "knäpp" in sv_text:
                    target["word_in_sentence"] = "knäpp"
                # Fix 'Okej då.' -> 'Okej då' in article 15
                elif target["word_in_sentence"] == "Okej då." and "Okej då" in sv_text:
                    target["word_in_sentence"] = "Okej då"
                # Fix 'hitta på' -> 'hitta' in article 0
                elif target["word_in_sentence"] == "hitta på" and "hitta" in sv_text:
                    target["word_in_sentence"] = "hitta"

            # Recalculate
            for target in sentence.get("target_words", []):
                word = target["word_in_sentence"]
                idx = sv_text.find(word)
                if idx != -1:
                    target["position_start"] = idx
                    target["position_end"] = idx + len(word)
                else:
                    print(f"STILL CANNOT FIND: {word} in {sv_text}")

with open("sfid_phase2_articles_v2.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Warnings fixed.")
