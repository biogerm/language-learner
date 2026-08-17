import json
import os

chunks_dir = "./course/sfid/phase3/data/chunks"

modified_count = 0
phrase_wipes = 0
gender_fixes = 0
verb_fixes = 0

for c in range(28, 55):
    meta_path = os.path.join(chunks_dir, f"meta_chunk_{c}.json")
    with open(meta_path, "r", encoding="utf-8") as f:
        meta_data = json.load(f)
        
    chunk_modified = False
    for word, entry in meta_data.items():
        # Rule 1: No phrase inflections if word contains space
        if ' ' in word:
            for field in ["verb_imperativ", "verb_presens", "verb_preteritum", "verb_supinum", "verb_perfekt_particip",
                          "adj_en", "adj_ett", "adj_plural", "adj_komparativ", "adj_superlativ"]:
                if entry[field] is not None:
                    entry[field] = None
                    chunk_modified = True
                    phrase_wipes += 1
            if entry["word_type"] == "noun":
                # Noun phrases with space should also have noun_gender set to null or appropriate if requested, but rule says "Return null for all inflection fields".
                pass
                
        # Rule 2: Compound noun gender check
        if entry["word_type"] == "noun":
            # Check common ett-endings
            ett_endings = ["ord", "rum", "verk", "program", "mål", "förbund", "slag", "hus", "ställe", "träd", "strå", "bageri", "centrum", "skap", "landsting", "skick", "manifest", "parti", "dopp", "fik", "råd", "dopp", "kafé", "bad", "skaldjur", "område", "slut", "samarbete", "departement", "bidrag", "tryck", "styre", "block", "statsråd", "kejsardöme", "parlament", "tuggmärke", "arrangemang", "krig", "ämne", "barndomsminne", "barnbarn"]
            # Exceptions for skap: kunskap (en), medlemskap (ett), osv.
            w_lower = word.lower()
            
            # Check if word ends with known ett words
            for ending in ["ord", "rum", "program", "förbund", "slag", "hus", "ställe", "träd", "strå", "centrum", "landsting", "skick", "manifest", "parti", "dopp", "fik", "råd", "skaldjur", "område", "slut", "samarbete", "departement", "bidrag", "skattetryck", "styre", "block", "statsråd", "kejsardöme", "parlament", "tuggmärke", "arrangemang", "krig", "ämne", "barndomsminne", "barnbarn"]:
                if w_lower.endswith(ending) and entry["noun_gender"] != "ett":
                    print(f"[Gender Fix] {word} in chunk {c}: changed gender from {entry['noun_gender']} to ett (ends with {ending})")
                    entry["noun_gender"] = "ett"
                    chunk_modified = True
                    gender_fixes += 1
                    
        # Rule 3: Group 2b verbs
        # Group 2b verbs end in k, p, t, s in stem and have preteritum in -te
        if entry["word_type"] == "verb" and entry["is_regular_verb"] is True and ' ' not in word:
            imp = entry["verb_imperativ"]
            pret = entry["verb_preteritum"]
            if imp and pret:
                # If imperativ ends in k, p, t, s and preteritum was set to -de instead of -te
                if imp[-1] in ['k', 'p', 't', 's']:
                    # Check if preteritum erroneously ends in 'de' instead of 'te'
                    if pret.endswith("de") and not pret.endswith("tde") and not pret.endswith("sde"):
                        # E.g., sök -> sökte, köp -> köpte, läs -> läste
                        corrected_pret = imp + "te"
                        if pret != corrected_pret:
                            print(f"[Verb Fix] {word} in chunk {c}: preteritum changed from {pret} to {corrected_pret}")
                            entry["verb_preteritum"] = corrected_pret
                            chunk_modified = True
                            verb_fixes += 1

    if chunk_modified:
        modified_count += 1
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta_data, f, ensure_ascii=False, indent=2)

print(f"Audit Complete! Modified {modified_count} files. Wiped {phrase_wipes} phrase inflections, fixed {gender_fixes} compound noun genders, fixed {verb_fixes} Group 2b verbs.")
