import json, re, glob

with open("course/sfid/phase5/contextual_en_discrepancies.json") as f:
    discrepancies = json.load(f)

# Load all articles into memory
articles = {}
for filepath in glob.glob("course/sfid/phase2/articles_translated/art_*.json"):
    with open(filepath) as f:
        art = json.load(f)
        articles[art["article_id"]] = art

# We want to check two things:
# 1. Did the article actually contain the word in a VALID way in another sentence?
# 2. Is the word truly ABSENT as a standalone word in the flagged sentence?

valid_in_article_count = 0
absent_as_standalone_count = 0
anomalies = []

for d in discrepancies:
    art_id = d["article"]
    s_id = d["sentence_id"]
    sv_word = d["sv_word"]  # This is the base_form
    
    art = articles[art_id]
    
    # Check 1: Is this sv_word validly used elsewhere in the article?
    # We look for a sentence in this article where this base_form is a target_word/secondary_word
    # AND it is NOT in the discrepancies list.
    validly_used = False
    for s in art.get("sentences", []):
        if s["sentence_id"] == s_id:
            continue # skip the flagged sentence
        
        # Check if sv_word is in this sentence's words
        word_found = False
        for w in s.get("target_words", []) + s.get("secondary_words", []):
            if w.get("base_form") == sv_word:
                word_found = True
                break
                
        if word_found:
            # Check if this sentence's usage was ALSO flagged as a discrepancy
            # If not, it means it's valid!
            is_flagged = any(x["sentence_id"] == s["sentence_id"] and x["sv_word"] == sv_word for x in discrepancies)
            if not is_flagged:
                validly_used = True
                break
                
    if validly_used:
        valid_in_article_count += 1
        
    # Check 2: Is the word TRULY absent as a standalone word in the flagged sentence?
    # We find the flagged sentence text.
    flagged_sentence = next(s for s in art.get("sentences", []) if s["sentence_id"] == s_id)
    sv_text = flagged_sentence["sv"]
    
    # We need the `word_in_sentence` to check if it's standalone
    word_in_sentence = ""
    for w in flagged_sentence.get("target_words", []) + flagged_sentence.get("secondary_words", []):
        if w.get("base_form") == sv_word:
            word_in_sentence = w.get("word_in_sentence", sv_word)
            break
            
    # Check if word_in_sentence exists as a standalone word
    # \b matches word boundaries, but Swedish letters åäö might need \b or \W
    # A safe way is to split by non-alphanumeric and check exact match
    words_in_text = re.findall(r'[a-zA-ZåäöÅÄÖ]+', sv_text.lower())
    
    if word_in_sentence.lower() not in words_in_text and sv_word.lower() not in words_in_text:
        absent_as_standalone_count += 1
    else:
        # It IS found as a standalone word!
        anomalies.append({
            "discrepancy": d,
            "sv_text": sv_text,
            "word_in_sentence": word_in_sentence,
            "words_in_text": words_in_text
        })

print(f"Total Discrepancies: {len(discrepancies)}")
print(f"Condition 1 (Appears validly elsewhere in the SAME article): {valid_in_article_count} / {len(discrepancies)}")
print(f"Condition 2 (TRULY ABSENT as standalone in the flagged sentence): {absent_as_standalone_count} / {len(discrepancies)}")

if anomalies:
    print(f"\nFound {len(anomalies)} anomalies where the word DOES exist as standalone but was flagged:")
    for a in anomalies[:5]:
        print(f"- {a['discrepancy']['sv_word']} in {a['discrepancy']['sentence_id']}")
        print(f"  Sentence: {a['sv_text']}")
