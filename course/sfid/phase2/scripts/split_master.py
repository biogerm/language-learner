import json, re

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
    with open("sfid_phase2_articles.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for stage in data.get("stages", []):
        for art in stage.get("articles", []):
            old_sentences = art.get("sentences", [])
            if len(old_sentences) != 1:
                continue
                
            full_text = old_sentences[0].get("sv", "")
            old_targets = old_sentences[0].get("target_words", [])
            article_id = art.get("article_id", "art_xx")
            
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
                    
                    if t_start >= s_info["global_start"] - len(full_text[s_info["global_start"]:].lstrip()) - 10 and t_start < s_info["global_end"] + 10:
                        rel_start = t_start - g_start
                        rel_end = t_end - g_start
                        
                        extracted = sv[max(0, rel_start):max(0, rel_end)]
                        expected = t["word_in_sentence"]
                        
                        if extracted != expected:
                            m = re.search(re.escape(expected), sv, re.IGNORECASE)
                            if m:
                                rel_start = m.start()
                                rel_end = m.end()
                                extracted = expected
                                
                        my_targets.append({
                            "word_in_sentence": extracted,
                            "base_form": t["base_form"],
                            "position_start": rel_start,
                            "position_end": rel_end
                        })
                
                new_sentences.append({
                    "sentence_id": s_id,
                    "sv": sv,
                    "en": "",
                    "target_words": my_targets
                })
                
            art["sentences"] = new_sentences
            
    with open("sfid_phase2_articles.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
    print("Master updated.")

if __name__ == "__main__":
    main()
