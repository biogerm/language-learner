import json, re, glob, os

with open("course/sfid/phase5/contextual_en_discrepancies.json") as f:
    discrepancies = json.load(f)

articles = {}
for filepath in glob.glob("course/sfid/phase2/articles_translated/art_*.json"):
    with open(filepath) as f:
        art = json.load(f)
        articles[art["article_id"]] = {"path": filepath, "data": art}

true_parasites = []
valid_words = []

for d in discrepancies:
    art_id = d["article"]
    s_id = d["sentence_id"]
    sv_word = d["sv_word"]
    art = articles[art_id]["data"]
    
    flagged_sentence = next(s for s in art.get("sentences", []) if s["sentence_id"] == s_id)
    sv_text = flagged_sentence["sv"]
    
    word_in_sentence = ""
    for w in flagged_sentence.get("target_words", []) + flagged_sentence.get("secondary_words", []):
        if w.get("base_form") == sv_word:
            word_in_sentence = w.get("word_in_sentence", sv_word)
            break
            
    words_in_text = re.findall(r'[a-zA-ZåäöÅÄÖ]+', sv_text.lower())
    
    if word_in_sentence.lower() not in words_in_text and sv_word.lower() not in words_in_text:
        true_parasites.append(d)
    else:
        valid_words.append({
            "discrepancy": d,
            "sv_text": sv_text,
            "word_in_sentence": word_in_sentence
        })

# 1. Analyze and clean the 131 true parasites
completely_missed = []
used_elsewhere = []

for p in true_parasites:
    art_id = p["article"]
    s_id = p["sentence_id"]
    sv_word = p["sv_word"]
    art = articles[art_id]["data"]
    
    # Check if used validly elsewhere
    validly_used = False
    for s in art.get("sentences", []):
        if s["sentence_id"] == s_id:
            continue
        
        word_found = False
        for w in s.get("target_words", []) + s.get("secondary_words", []):
            if w.get("base_form") == sv_word:
                word_found = True
                break
        
        if word_found:
            is_flagged = any(x["sentence_id"] == s["sentence_id"] and x["sv_word"] == sv_word for x in true_parasites)
            if not is_flagged:
                validly_used = True
                break
                
    if validly_used:
        used_elsewhere.append(p)
    else:
        # Check if the word is actually in the true target list for this article
        completely_missed.append(p)

    # DELETE the parasite
    s_obj = next(s for s in art.get("sentences", []) if s["sentence_id"] == s_id)
    if "target_words" in s_obj:
        s_obj["target_words"] = [w for w in s_obj["target_words"] if w.get("base_form") != sv_word]
    if "secondary_words" in s_obj:
        s_obj["secondary_words"] = [w for w in s_obj["secondary_words"] if w.get("base_form") != sv_word]

print("=== COMPLETELY MISSED WORDS (Never validly used in the article) ===")
# Deduplicate for display
missed_set = set()
for m in completely_missed:
    k = f"{m['article']}: {m['sv_word']}"
    if k not in missed_set:
        missed_set.add(k)
        print(f"- {k} (Falsely tagged in {m['sentence_id']})")
print(f"Total unique missed: {len(missed_set)}")

# Write updated articles (parasites removed)
for art_info in articles.values():
    with open(art_info["path"], "w") as f:
        json.dump(art_info["data"], f, indent=4, ensure_ascii=False)

# Prepare a list of the 122 valid words for LLM fix
with open("course/sfid/phase5/valid_discrepancies_to_fix.json", "w") as f:
    json.dump(valid_words, f, indent=4, ensure_ascii=False)

print(f"\nRemoved {len(true_parasites)} true parasites from JSONs.")
print(f"Saved {len(valid_words)} valid words to valid_discrepancies_to_fix.json for LLM processing.")
