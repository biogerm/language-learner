import json
import glob
import re

files = ["articles_translated/art_31.json", "articles_translated/art_47.json", "articles_translated/art_00.json"]

for filepath in files:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    modified = False
    for s in data["sentences"]:
        sv = s["sv"]
        for tw in s.get("target_words", []):
            start = tw["position_start"]
            end = tw["position_end"]
            extracted = sv[start:end]
            if extracted.lower() != tw["word_in_sentence"].lower():
                # We have a mismatch!
                bf = tw["base_form"]
                
                # Let's try to find base_form
                idx = sv.lower().find(bf.lower())
                if idx != -1:
                    tw["position_start"] = idx
                    tw["position_end"] = idx + len(bf)
                    tw["word_in_sentence"] = sv[idx:idx+len(bf)]
                    modified = True
                else:
                    # If base form is not found, maybe just use the first word of base_form
                    first_word = bf.split()[0]
                    idx = sv.lower().find(first_word.lower())
                    if idx != -1:
                        tw["position_start"] = idx
                        tw["position_end"] = idx + len(first_word)
                        tw["word_in_sentence"] = sv[idx:idx+len(first_word)]
                        modified = True
                    else:
                        print(f"Could not fix {bf} in {sv}")
                        
    if modified:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
print("Fix script completed.")
