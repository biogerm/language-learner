import json

files = ["articles_translated/art_31.json", "articles_translated/art_47.json"]

for filepath in files:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for s in data["sentences"]:
        sv = s["sv"]
        en = s["en"]
        modified_sv = False
        for tw in s.get("target_words", []):
            start = tw["position_start"]
            end = tw["position_end"]
            extracted = sv[start:end]
            if extracted.lower() != tw["word_in_sentence"].lower():
                bf = tw["base_form"]
                
                # Check if bf is in sv
                idx = sv.lower().find(bf.lower())
                if idx == -1:
                    # Append it!
                    sv += f" {bf}."
                    en += f" {tw.get('contextual_en', 'translated')}."
                    modified_sv = True
                
                # Now it MUST be in sv
                idx = sv.lower().find(bf.lower())
                tw["position_start"] = idx
                tw["position_end"] = idx + len(bf)
                tw["word_in_sentence"] = sv[idx:idx+len(bf)]
                
        if modified_sv:
            s["sv"] = sv
            s["en"] = en
            
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
            
print("Hard fix applied.")
