import json, glob

with open("course/sfid/phase4/output/audio_manifest.json") as f:
    manifest = json.load(f)

word_audio_keys = set(manifest.get("words", {}).keys())

missing_target_audio = []
missing_secondary_audio = []

for filepath in glob.glob("course/sfid/phase2/articles_translated/art_*.json"):
    with open(filepath, "r") as f:
        art = json.load(f)
    for s in art.get("sentences", []):
        for w in s.get("target_words", []):
            if w.get("base_form") not in word_audio_keys:
                missing_target_audio.append(w.get("base_form"))
        for w in s.get("secondary_words", []):
            if w.get("base_form") not in word_audio_keys:
                missing_secondary_audio.append(w.get("base_form"))

missing_target_audio = list(set(missing_target_audio))
missing_secondary_audio = list(set(missing_secondary_audio))

print(f"Target words missing audio: {len(missing_target_audio)}")
print(f"Secondary words missing audio: {len(missing_secondary_audio)}")

# Also check missing contextual_en for target words
missing_contextual_en_art19 = []
missing_contextual_en_others = []
for filepath in glob.glob("course/sfid/phase2/articles_translated/art_*.json"):
    with open(filepath, "r") as f:
        art = json.load(f)
    is_art19 = "art_19" in filepath
    for s in art.get("sentences", []):
        for w in s.get("target_words", []):
            if not w.get("contextual_en"):
                if is_art19:
                    missing_contextual_en_art19.append(w.get("base_form"))
                else:
                    missing_contextual_en_others.append(w.get("base_form"))

print(f"Target words missing contextual_en in art_19: {len(missing_contextual_en_art19)}")
print(f"Target words missing contextual_en in other articles: {len(missing_contextual_en_others)}")

