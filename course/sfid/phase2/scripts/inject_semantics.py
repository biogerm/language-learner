import json
import glob
import os
import re

def inject():
    # Load all semantic mappings
    mapping = {}
    for i in ["b1", "b2", "b3", "patch"]:
        fpath = f"sem_{i}.json"
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    mapping.update(data)
                except Exception as e:
                    print(f"Error loading {fpath}: {e}")
                    
    if not mapping:
        print("No semantic mappings found.")
        return

    stats = {"processed_articles": 0, "target_words_injected": 0, "secondary_words_added": 0, "errors": []}
    files = sorted(glob.glob("articles_translated/art_*.json"))
    
    for filepath in files:
        with open(filepath, "r", encoding="utf-8") as f:
            art_data = json.load(f)
            
        modified = False
        for s in art_data["sentences"]:
            sid = s["sentence_id"]
            if sid in mapping:
                modified = True
                s_map = mapping[sid]
                
                # Update target words
                t_map = s_map.get("target_words", {})
                for tw in s.get("target_words", []):
                    sv_w = tw["word_in_sentence"]
                    if sv_w in t_map:
                        tw["contextual_en"] = t_map[sv_w]
                        stats["target_words_injected"] += 1
                    else:
                        stats["errors"].append(f"[{sid}] Missing contextual_en for target word '{sv_w}'")

                # Add secondary words
                sec_map = s_map.get("secondary_words", {})
                if isinstance(sec_map, list):
                    sec_map = {}
                new_sec_words = []
                sv_text = s["sv"]
                
                for sv_w, en_w in sec_map.items():
                    # Find exact match with word boundaries if possible, else fallback to standard find
                    pattern = r'\b' + re.escape(sv_w) + r'\b'
                    match = re.search(pattern, sv_text, re.IGNORECASE)
                    
                    if match:
                        start, end = match.span()
                        new_sec_words.append({
                            "word_in_sentence": sv_text[start:end],
                            "base_form": sv_text[start:end].lower(),
                            "position_start": start,
                            "position_end": end,
                            "contextual_en": en_w
                        })
                        stats["secondary_words_added"] += 1
                    else:
                        # Fallback for words with attached punctuation etc.
                        idx = sv_text.lower().find(sv_w.lower())
                        if idx != -1:
                            end = idx + len(sv_w)
                            new_sec_words.append({
                                "word_in_sentence": sv_text[idx:end],
                                "base_form": sv_w.lower(),
                                "position_start": idx,
                                "position_end": end,
                                "contextual_en": en_w
                            })
                            stats["secondary_words_added"] += 1
                        else:
                            stats["errors"].append(f"[{sid}] Secondary word '{sv_w}' not found in sentence.")
                            
                s["secondary_words"] = new_sec_words
                
        if modified:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(art_data, f, ensure_ascii=False, indent=4)
            stats["processed_articles"] += 1
            
    print(f"\n--- Injection Statistics ---")
    print(f"Articles updated: {stats['processed_articles']}")
    print(f"Target words injected: {stats['target_words_injected']}")
    print(f"Secondary words added: {stats['secondary_words_added']}")
    if stats["errors"]:
        print(f"Encountered {len(stats['errors'])} errors (e.g. missing words). See log.")
        with open("injection_errors.log", "w", encoding="utf-8") as f:
            f.write("\n".join(stats["errors"]))
    else:
        print("0 errors! Perfect injection.")

if __name__ == "__main__":
    inject()
