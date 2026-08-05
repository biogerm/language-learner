import json
import glob

all_translations = {}
for i in range(6):
    filename = f"translations_{i}.json"
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_translations.update(data)
    except FileNotFoundError:
        print(f"Missing {filename}")

print(f"Total sentences translated: {len(all_translations)}")
with open("all_translations_raw.json", "w", encoding="utf-8") as f:
    json.dump(all_translations, f, ensure_ascii=False, indent=2)

