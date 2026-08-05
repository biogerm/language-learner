import json, glob, re

def get_target_intervals(targets):
    intervals = []
    for t in targets:
        intervals.append((t["position_start"], t["position_end"]))
    return intervals

def is_inside_target(idx, intervals):
    for start, end in intervals:
        if start < idx < end:
            return True
    return False

def split_text_into_sentences(text, targets):
    intervals = get_target_intervals(targets)
    boundaries = [0]
    
    # We also want to keep dialogues together if possible? 
    # Just avoiding splitting inside target intervals is a huge win.
    for match in re.finditer(r'[.!?]”?"?\s+(?=["”A-ZÅÄÖ])', text):
        idx = match.end()
        if not is_inside_target(idx, intervals):
            boundaries.append(idx)
    boundaries.append(len(text))
    
    sentences_info = []
    for i in range(len(boundaries)-1):
        raw_start = boundaries[i]
        raw_end = boundaries[i+1]
        raw_str = text[raw_start:raw_end]
        
        stripped_str = raw_str.strip()
        if not stripped_str:
            continue
            
        leading_ws = len(raw_str) - len(raw_str.lstrip())
        global_start = raw_start + leading_ws
        global_end = global_start + len(stripped_str)
        
        sentences_info.append({
            "sv": stripped_str,
            "global_start": global_start,
            "global_end": global_end
        })
        
    return sentences_info

def main():
    article_files = glob.glob("articles/article_*.json")
    for file_path in article_files:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        if isinstance(data, list):
            article_ref = data[0] if len(data) > 0 else {}
        elif "stages" in data:
            article_ref = data["stages"][0]["articles"][0]
        else:
            article_ref = data
            
        old_sentences = article_ref.get("sentences", [])
        if len(old_sentences) != 1:
            continue
            
        full_text = old_sentences[0].get("sv", "")
        old_targets = old_sentences[0].get("target_words", [])
        article_id = article_ref.get("article_id", "art_xx")
        
        sentences_info = split_text_into_sentences(full_text, old_targets)
        new_sentences = []
        
        for idx, s_info in enumerate(sentences_info):
            s_id = f"{article_id}_s{idx+1:03d}"
            sv = s_info["sv"]
            g_start = s_info["global_start"]
            g_end = s_info["global_end"]
            
            my_targets = []
            for t in old_targets:
                t_start = t["position_start"]
                t_end = t["position_end"]
                
                # if target overlaps with this sentence at all
                # ideally target is fully inside. 
                if t_start >= s_info["global_start"] - len(full_text[s_info["global_start"]:].lstrip()) - 10 and t_start < s_info["global_end"] + 10:
                    # we will do a smart re-alignment if it's slightly off
                    # First, calculate relative
                    rel_start = t_start - g_start
                    rel_end = t_end - g_start
                    
                    # check if it matches
                    extracted = sv[max(0, rel_start):max(0, rel_end)]
                    expected = t["word_in_sentence"]
                    
                    if extracted != expected:
                        # find it in the sentence
                        import re
                        m = re.search(re.escape(expected), sv, re.IGNORECASE)
                        if m:
                            rel_start = m.start()
                            rel_end = m.end()
                            extracted = expected
                        else:
                            # if not found, it means the teacher changed the text but not the target_word list
                            # we update the expected to what's at the offset, or we just keep it if it's a known discrepancy
                            pass
                            
                    my_targets.append({
                        "word_in_sentence": extracted, # if it wasn't found, keep extracted
                        "base_form": t["base_form"],
                        "position_start": rel_start,
                        "position_end": rel_end
                    })
                    if extracted != expected:
                         print(f"Mismatch fixed/remains in {file_path}: expected '{expected}', now '{extracted}'")
            
            new_sentences.append({
                "sentence_id": s_id,
                "sv": sv,
                "en": "",
                "target_words": my_targets
            })
            
        article_ref["sentences"] = new_sentences
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
    print("Done splitting sentences.")

if __name__ == "__main__":
    main()
