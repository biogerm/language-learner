import json
import os

chunks_dir = "./course/sfid/phase3/data/chunks"

fixes = {
    "tevebolag": "ett",      # ett bolag
    "apelsinträd": "ett",    # ett träd
    "kulturella band": "ett" # ett band
}

for c in range(28, 55):
    meta_path = os.path.join(chunks_dir, f"meta_chunk_{c}.json")
    with open(meta_path, "r", encoding="utf-8") as f:
        meta_data = json.load(f)
    modified = False
    for word, entry in meta_data.items():
        if word in fixes and entry["noun_gender"] != fixes[word]:
            print(f"Correcting {word} in chunk {c}: {entry['noun_gender']} -> {fixes[word]}")
            entry["noun_gender"] = fixes[word]
            modified = True
    if modified:
        with open(meta_path, "w", encoding="utf-8") as fw:
            json.dump(meta_data, fw, ensure_ascii=False, indent=2)

