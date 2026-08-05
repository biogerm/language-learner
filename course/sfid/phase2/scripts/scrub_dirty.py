import json, os, glob

def main():
    dirty_english = ["eyes,", "freedom", "have", "minded", "ntally", "write"]
    dirty_swedish = ["blunda", "frihet", "ha", "öppensinnad", "mentalt", "skriva"]
    
    # Clean master dictionary
    dict_path = "../phase1/master_dictionary.json"
    with open(dict_path, "r", encoding="utf-8") as f:
        master_dict = json.load(f)
        
    removed = []
    for w in dirty_english + dirty_swedish:
        if w in master_dict:
            del master_dict[w]
            removed.append(w)
            
    with open(dict_path, "w", encoding="utf-8") as f:
        json.dump(master_dict, f, indent=2, ensure_ascii=False)
    print(f"Removed from master_dictionary: {removed}")
    
    # Clean articles
    article_files = glob.glob("articles/article_*.json")
    scrubbed_count = 0
    for file_path in article_files:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        changed = False
        
        # Determine structure
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
            targets = sentence.get("target_words", [])
            new_targets = []
            for t in targets:
                if t["base_form"] in dirty_swedish or t["base_form"] in dirty_english:
                    print(f"Scrubbing {t['base_form']} from {file_path}")
                    changed = True
                    scrubbed_count += 1
                else:
                    new_targets.append(t)
            sentence["target_words"] = new_targets
            
        # Clean primary/secondary tracking too!
        if "primary_words_used" in article_ref:
            new_p = [w for w in article_ref["primary_words_used"] if w not in dirty_swedish and w not in dirty_english]
            if len(new_p) != len(article_ref["primary_words_used"]): changed = True
            article_ref["primary_words_used"] = new_p
        
        if changed:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                
    print(f"Scrubbed {scrubbed_count} dirty references from articles.")

if __name__ == "__main__":
    main()
