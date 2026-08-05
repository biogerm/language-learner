import json
import sys
import string

def loose_match(contextual_en, full_en):
    if not contextual_en or not full_en:
        return False
    ctx_words = [w.strip(string.punctuation).lower() for w in contextual_en.split()]
    full_words = [w.strip(string.punctuation).lower() for w in full_en.split()]
    for cw in ctx_words:
        if not cw: continue
        if any(cw in fw or fw in cw for fw in full_words):
            return True
    return False

def validate_json(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[Error] Invalid JSON format in {filepath}: {e}")
        sys.exit(1)

    if isinstance(data, dict):
        if "sentences" in data:
            sentences = data["sentences"]
        else:
            sentences = []
            for v in data.values():
                if isinstance(v, list):
                    sentences.extend(v)
    else:
        sentences = data

    errors = []
    
    for i, s in enumerate(sentences):
        sid = s.get("sentence_id", f"idx_{i}")
        sv = s.get("sv", "")
        en = s.get("en", "")
        
        target_words = s.get("target_words", [])
        secondary_words = s.get("secondary_words", [])
        
        for w_type, word_list in [("target_words", target_words), ("secondary_words", secondary_words)]:
            for w in word_list:
                word_in_sen = w.get("word_in_sentence", "")
                base_form = w.get("base_form", "")
                ctx_en = w.get("contextual_en", "")
                start = w.get("position_start")
                end = w.get("position_end")
                
                if start is None or end is None:
                    errors.append(f"[{sid}] Missing position indices for '{word_in_sen}'.")
                    continue
                
                extracted = sv[start:end]
                if extracted.lower() != word_in_sen.lower():
                    errors.append(f"[{sid}] Index mismatch for '{word_in_sen}': extracted '{extracted}' at {start}:{end}.")
                    
                if not ctx_en:
                    errors.append(f"[{sid}] Missing contextual_en for '{word_in_sen}'.")

    if errors:
        for err in errors:
            print(f"[ValidationError] {err}")
        print("\nFix these errors and run the script again!")
        sys.exit(1)
        
    print(f"[Success] {filepath} passed all strict validations!")
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_enrichment.py <json_file>")
        sys.exit(1)
    validate_json(sys.argv[1])
