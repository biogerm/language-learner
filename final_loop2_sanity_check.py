import json
import os

chunks_dir = "./course/sfid/phase3/data/chunks"

total_words = 0
total_phrases = 0

for c in range(28, 55):
    deep_path = os.path.join(chunks_dir, f"deep_chunk_{c}.json")
    meta_path = os.path.join(chunks_dir, f"meta_chunk_{c}.json")
    
    assert os.path.exists(deep_path), f"Missing {deep_path}"
    assert os.path.exists(meta_path), f"Missing {meta_path}"
    
    with open(deep_path, "r", encoding="utf-8") as f:
        deep_words = json.load(f)
    with open(meta_path, "r", encoding="utf-8") as f:
        meta_data = json.load(f)
        
    assert len(deep_words) == len(meta_data), f"Chunk {c} mismatch: {len(deep_words)} vs {len(meta_data)}"
    
    for w in deep_words:
        assert w in meta_data, f"Chunk {c}: word '{w}' missing in meta"
        entry = meta_data[w]
        total_words += 1
        
        wt = entry["word_type"]
        assert wt in ["noun", "verb", "adjective"], f"Invalid word_type '{wt}' for '{w}'"
        
        has_space = (' ' in w)
        if has_space:
            total_phrases += 1
            
        if wt == "noun":
            assert entry["noun_gender"] in ["en", "ett"], f"Chunk {c}: Noun '{w}' has invalid gender '{entry['noun_gender']}'"
            assert entry["is_regular_verb"] is None
            assert entry["verb_imperativ"] is None
            assert entry["verb_presens"] is None
            assert entry["verb_preteritum"] is None
            assert entry["verb_supinum"] is None
            assert entry["verb_perfekt_particip"] is None
            assert entry["adj_en"] is None
            assert entry["adj_ett"] is None
            assert entry["adj_plural"] is None
            assert entry["adj_komparativ"] is None
            assert entry["adj_superlativ"] is None
        elif wt == "verb":
            assert entry["noun_gender"] is None
            assert entry["is_regular_verb"] in [True, False]
            assert entry["adj_en"] is None
            assert entry["adj_ett"] is None
            assert entry["adj_plural"] is None
            assert entry["adj_komparativ"] is None
            assert entry["adj_superlativ"] is None
            if has_space:
                assert entry["verb_imperativ"] is None, f"Phrase verb '{w}' must have null verb_imperativ"
                assert entry["verb_presens"] is None, f"Phrase verb '{w}' must have null verb_presens"
                assert entry["verb_preteritum"] is None, f"Phrase verb '{w}' must have null verb_preteritum"
                assert entry["verb_supinum"] is None, f"Phrase verb '{w}' must have null verb_supinum"
                assert entry["verb_perfekt_particip"] is None, f"Phrase verb '{w}' must have null verb_perfekt_particip"
            else:
                assert entry["verb_imperativ"] is not None, f"Single verb '{w}' missing imperativ"
                assert entry["verb_presens"] is not None, f"Single verb '{w}' missing presens"
                assert entry["verb_preteritum"] is not None, f"Single verb '{w}' missing preteritum"
                assert entry["verb_supinum"] is not None, f"Single verb '{w}' missing supinum"
        elif wt == "adjective":
            assert entry["noun_gender"] is None
            assert entry["is_regular_verb"] is None
            assert entry["verb_imperativ"] is None
            assert entry["verb_presens"] is None
            assert entry["verb_preteritum"] is None
            assert entry["verb_supinum"] is None
            assert entry["verb_perfekt_particip"] is None
            if has_space:
                assert entry["adj_en"] is None, f"Phrase adj '{w}' must have null adj_en"
                assert entry["adj_ett"] is None, f"Phrase adj '{w}' must have null adj_ett"
                assert entry["adj_plural"] is None, f"Phrase adj '{w}' must have null adj_plural"
                assert entry["adj_komparativ"] is None, f"Phrase adj '{w}' must have null adj_komparativ"
                assert entry["adj_superlativ"] is None, f"Phrase adj '{w}' must have null adj_superlativ"
            else:
                assert entry["adj_en"] is not None, f"Single adj '{w}' missing adj_en"
                assert entry["adj_ett"] is not None, f"Single adj '{w}' missing adj_ett"
                assert entry["adj_plural"] is not None, f"Single adj '{w}' missing adj_plural"
                assert entry["adj_komparativ"] is not None, f"Single adj '{w}' missing adj_komparativ"
                assert entry["adj_superlativ"] is not None, f"Single adj '{w}' missing adj_superlativ"

print(f"SANITY CHECK PASSED PERFECTLY!")
print(f"Total files checked: 27 (chunks 28 to 54)")
print(f"Total words validated: {total_words}")
print(f"Total phrases validated (all inflections = null): {total_phrases}")
