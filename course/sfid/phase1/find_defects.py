import json
import re

def main():
    with open("../data/b1_ordlista.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    defects = {
        "rule_3_1_soft_hyphen": [],
        "rule_3_2_grammar": [],
        "rule_3_3_phrasal_verbs": [],
        "rule_3_4_orphans": [],
        "missing_translation": []
    }
    
    particles = {"på", "av", "ut", "upp", "till", "om", "med", "in", "för", "från", "åt", "över", "ihop", "fram", "bort", "med", "ner", "kvar"}
    
    for key, value in data.items():
        if value is None or str(value).strip() == "":
            defects["missing_translation"].append(key)
            continue
            
        value = str(value).strip()
        
        # Rule 3.4: Orphans
        if len(key) < 5 and re.match(r'^[a-zA-Z]+$', key):
            # Might be an orphan, let's be careful not to delete real words like "att", "bra", "bok" etc.
            # But the rule says: length < 5 and only english characters. But "att", "bra" are valid words.
            # Wait, the spec says "This kind of entry is usually caused by PDF extraction fragments. For example 'ne': 'well known', 'ty': 'flower', 'me': 'my jacket?'"
            # Actually, "bra" has a translation. PDF fragments usually have weird translations or are just fragments.
            # Let's just flag them for review instead of auto-deleting if we are manually fixing as LLM.
            if len(key) <= 3 and value.islower() and not value.startswith("to "): 
                # just a heuristic to flag them
                defects["rule_3_4_orphans"].append((key, value))
        
        # Rule 3.1: Soft hyphen
        if "\u00ad" in value:
            defects["rule_3_1_soft_hyphen"].append((key, value))
            
        # Rule 3.2: Grammar info
        if value.startswith("(-") or value.startswith("(+"):
            defects["rule_3_2_grammar"].append((key, value))
            
        # Rule 3.3: Phrasal verbs
        if value.lower() in particles:
            defects["rule_3_3_phrasal_verbs"].append((key, value))

    with open("defects.json", "w", encoding="utf-8") as f:
        json.dump(defects, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
