import json
import os

chunks_dir = "./course/sfid/phase3/data/chunks"

# Known Swedish gender dictionary for verification
known_genders = {
    # Chunk 35 & 43 fix
    "kollektivtrafik": "en",
    "högertrafik": "en",
    "trafik": "en",
    
    # Let's inspect all nouns across chunks 28 to 54
}

for c in range(28, 55):
    meta_path = os.path.join(chunks_dir, f"meta_chunk_{c}.json")
    with open(meta_path, "r", encoding="utf-8") as f:
        meta_data = json.load(f)
        
    for w, entry in meta_data.items():
        if entry["word_type"] == "noun":
            g = entry["noun_gender"]
            if w in known_genders and g != known_genders[w]:
                print(f"Fixing {w} in chunk {c}: {g} -> {known_genders[w]}")
                entry["noun_gender"] = known_genders[w]
                with open(meta_path, "w", encoding="utf-8") as fw:
                    json.dump(meta_data, fw, ensure_ascii=False, indent=2)

