import json

def find_word_in_text(word, text):
    import re
    pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
    match = pattern.search(text)
    if match:
        return match.start(), match.end(), match.group(0)
    pattern_raw = re.compile(re.escape(word), re.IGNORECASE)
    match = pattern_raw.search(text)
    if match:
        return match.start(), match.end(), match.group(0)
    return -1, -1, None

def main():
    dirty_english = ["eyes,", "freedom", "have", "minded", "ntally", "write"]
    dirty_swedish = ["blunda", "frihet", "ha", "öppensinnad", "mentalt", "skriva"]
    cat1_words = ["Hur många?", "Varför", "en och en halv", "faktisk", "i mitten av", 
                  "kombinera", "komma tillbaka", "lika många", "lämplig", "respektive", "toppa"]

    with open("sfid_phase2_articles.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    scrubbed = 0
    added = 0
    
    for stage in data.get("stages", []):
        for art in stage.get("articles", []):
            for sentence in art.get("sentences", []):
                sv_text = sentence.get("sv", "")
                targets = sentence.get("target_words", [])
                new_targets = []
                for t in targets:
                    if t["base_form"] in dirty_english + dirty_swedish:
                        scrubbed += 1
                    else:
                        new_targets.append(t)
                        
                existing_bases = [t["base_form"] for t in new_targets]
                for w in cat1_words:
                    if w not in existing_bases:
                        s, e, m = find_word_in_text(w, sv_text)
                        if s != -1:
                            new_targets.append({
                                "word_in_sentence": m,
                                "base_form": w,
                                "position_start": s,
                                "position_end": e
                            })
                            added += 1
                new_targets.sort(key=lambda x: x["position_start"])
                sentence["target_words"] = new_targets
                
            if "primary_words_used" in art:
                art["primary_words_used"] = [w for w in art["primary_words_used"] if w not in dirty_english + dirty_swedish]

    with open("sfid_phase2_articles.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
    print(f"Master db: scrubbed {scrubbed}, added {added}")

if __name__ == "__main__":
    main()
