import json, os, glob, re

def find_word_in_text(word, text):
    # simple case insensitive search, return start and end index
    pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
    match = pattern.search(text)
    if match:
        return match.start(), match.end(), match.group(0)
    
    # fallback for things like "Hur många?"
    pattern_raw = re.compile(re.escape(word), re.IGNORECASE)
    match = pattern_raw.search(text)
    if match:
        return match.start(), match.end(), match.group(0)
    return -1, -1, None

def main():
    dirty_english = ["eyes,", "freedom", "have", "minded", "ntally", "write"]
    
    # 1. Clean master dictionary
    dict_path = "../phase1/master_dictionary.json"
    with open(dict_path, "r", encoding="utf-8") as f:
        master = json.load(f)
        
    removed = []
    if "words" in master:
        for w in dirty_english:
            if w in master["words"]:
                del master["words"][w]
                removed.append(w)
        master["metadata"]["total_words"] -= len(removed)
            
    with open(dict_path, "w", encoding="utf-8") as f:
        json.dump(master, f, indent=2, ensure_ascii=False)
    print(f"Removed from master_dictionary: {removed}")
    
    # 2. Check and highlight Category 1 words
    cat1_words = ["Hur många?", "Varför", "en och en halv", "faktisk", "i mitten av", 
                  "kombinera", "komma tillbaka", "lika många", "lämplig", "respektive", "toppa"]
                  
    article_files = glob.glob("articles/article_*.json")
    scrubbed_count = 0
    added_count = 0
    
    for file_path in article_files:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        changed = False
        
        # Structure handling
        if isinstance(data, list):
            sentences = data[0].get("sentences", []) if len(data) > 0 else []
            article_ref = data[0] if len(data) > 0 else {}
        elif "stages" in data:
            article_ref = data["stages"][0]["articles"][0]
            sentences = article_ref.get("sentences", [])
        else:
            article_ref = data
            sentences = article_ref.get("sentences", [])
            
        for sentence in sentences:
            sv_text = sentence.get("sv", "")
            targets = sentence.get("target_words", [])
            new_targets = []
            
            # Scrub dirty words
            for t in targets:
                # also scrub the fixed swedish translations if they were added as base_forms because they don't exist in dict
                if t["base_form"] in dirty_english + ["blunda", "frihet", "ha", "öppensinnad", "mentalt", "skriva"]:
                    print(f"Scrubbing {t['base_form']} from {file_path}")
                    changed = True
                    scrubbed_count += 1
                else:
                    new_targets.append(t)
            
            # Add missing cat1 words
            existing_bases = [t["base_form"] for t in new_targets]
            for w in cat1_words:
                if w not in existing_bases:
                    s_idx, e_idx, matched_str = find_word_in_text(w, sv_text)
                    if s_idx != -1:
                        print(f"Found missing Category 1 word '{w}' in {file_path}. Adding to target_words.")
                        new_targets.append({
                            "word_in_sentence": matched_str,
                            "base_form": w,
                            "position_start": s_idx,
                            "position_end": e_idx
                        })
                        changed = True
                        added_count += 1
                        
            # sort targets by position
            new_targets.sort(key=lambda x: x["position_start"])
            sentence["target_words"] = new_targets
            
        # Clean primary/secondary tracking
        dirty_swedish = ["blunda", "frihet", "ha", "öppensinnad", "mentalt", "skriva"]
        if "primary_words_used" in article_ref:
            new_p = [w for w in article_ref["primary_words_used"] if w not in dirty_swedish and w not in dirty_english]
            # add the found ones to secondary if they aren't there
            if len(new_p) != len(article_ref["primary_words_used"]): changed = True
            article_ref["primary_words_used"] = new_p
            
        if changed:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                
    print(f"Scrubbed {scrubbed_count} dirty references.")
    print(f"Added {added_count} missing Category 1 words back into tracking.")

if __name__ == "__main__":
    main()
