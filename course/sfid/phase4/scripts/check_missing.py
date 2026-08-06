import json, os

with open("output/audio_manifest.json") as f:
    m = json.load(f)

missing_sentences = []
for k, v in m["sentences"].items():
    if not os.path.exists("output/" + v["file"]):
        missing_sentences.append(k)

missing_words = []
for k, v in m["words"].items():
    if not os.path.exists("output/" + v["file"]):
        missing_words.append(k)

print(f"Missing sentences: {len(missing_sentences)}")
print(f"Missing words: {len(missing_words)}")

with open("output/missing_audio.json", "w") as f:
    json.dump({"sentences": missing_sentences, "words": missing_words}, f, indent=2)

print("\nSample missing sentences:")
for s in missing_sentences[:5]: print(s)

print("\nSample missing words:")
for w in missing_words[:5]: print(w)
