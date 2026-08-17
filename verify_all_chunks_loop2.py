import json
import os

chunks_dir = "./course/sfid/phase3/data/chunks"

errors = []
total_words = 0
space_words = 0
inflections_on_space_words = 0

for c in range(28, 55):
    meta_path = os.path.join(chunks_dir, f"meta_chunk_{c}.json")
    assert os.path.exists(meta_path), f"Missing {meta_path}"
    
    with open(meta_path, "r", encoding="utf-8") as f:
        meta_data = json.load(f)
        
    for w, entry in meta_data.items():
        total_words += 1
        
        # Rule 1: No phrase inflections if space in word
        if ' ' in w:
            space_words += 1
            inflection_fields = ["verb_imperativ", "verb_presens", "verb_preteritum", "verb_supinum", "verb_perfekt_particip",
                                 "adj_en", "adj_ett", "adj_plural", "adj_komparativ", "adj_superlativ"]
            for field in inflection_fields:
                if entry[field] is not None:
                    inflections_on_space_words += 1
                    errors.append(f"Chunk {c}: Word '{w}' has space but {field} is not null: {entry[field]}")

print(f"Total words: {total_words}")
print(f"Words with spaces: {space_words}")
print(f"Inflections on space words: {inflections_on_space_words}")
if errors:
    print(f"\nERRORS FOUND ({len(errors)}):")
    for err in errors[:20]:
        print(" ", err)
else:
    print("\nSUCCESS: All space words have null inflections across chunks 28-54!")

