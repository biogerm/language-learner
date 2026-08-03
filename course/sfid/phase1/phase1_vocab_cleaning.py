import json
import os
from datetime import datetime

def main():
    input_path = "../data/b1_ordlista.json"
    output_path = "master_dictionary.json"
    log_path = "dictionary_cleaning.log"
    stats_path = "phase1_statistics.md"
    
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    log_file = open(log_path, "w", encoding="utf-8")
    
    def log_change(rule, original_key, original_val, new_key, new_val):
        log_file.write(f"[{rule}] {original_key}: {original_val} -> {new_key}: {new_val}\n")
    
    # Manual fixes by the AI/LLM based on PDF extraction context
    fixes_3_1_and_3_2 = {
        "människa": "human being, person",
        "jag har alltid varit intresserad av…": "I have always been interested",
        "förbereda sig": "prepare oneself",
        "kulturpersonlighet": "cultural persona, someone well known in the arts/culture",
        "Har du hört vad som har hänt?": "Have you heard what’s happened?",
        "partikel": "grammatical particle",
        "Vet du vad jag gjorde igår…?": "Do you know what I did yesterday?",
        "sockerbagare": "confectioner",
        "finansminister": "minister of finance",
        "tilläggspension": "supplementary, income-based pension",
        "funktionshinder": "disability",
        "dagdrömma": "daydream",
        "skådespelerska": "actress",
        "släktkrönika": "family chronicle",
        "landskapsblomma": "official county flower",
        "mountainbike": "mountain bike",
        "lokalproducerad": "locally produced",
        "konst- och industriutställning": "art and industrial exhibition",
        "ingå partnerskap": "enter into a civil union",
        "vetenskapsman": "scientist",
        "Jag måste berätta en sak/en grej…": "I have to tell you something",
        "beställa tid": "make an appointment",
        "Vilken tur att du påminde mig": "How fortunate that you reminded me",
        "kvadratkilometer": "square kilometer",
        "miljömedveten": "environmentally conscious",
        "sammanfatta": "summarize",
        "karensdag": "qualifying day for sickness benefit",
        "parlamentsledamot": "member of parliament",
        "Filmen bygger på en verklig händelse.": "The movie is based on a true story."
    }
    
    fragments_to_delete = {"ne", "ter", "sed", "ty", "on", "of", "na)", "nen)"}
    
    phrasal_verbs_fixes = {
        "ringa": ("ringa in", "call in"),
        "stöta": ("stöta på", "bump into, encounter")
    }
    
    stats = {
        "total_input": len(data),
        "rule_3_1_and_3_2_fixed": 0,
        "rule_3_3_fixed": 0,
        "rule_3_4_deleted": 0,
        "total_output": 0
    }
    
    cleaned_dict = {}
    
    for key, value in data.items():
        if key in fragments_to_delete:
            log_change("RULE 3.4", key, value, "[DELETED]", "[DELETED]")
            stats["rule_3_4_deleted"] += 1
            continue
            
        if key in fixes_3_1_and_3_2:
            new_val = fixes_3_1_and_3_2[key]
            log_change("RULE 3.1 / 3.2", key, value, key, new_val)
            cleaned_dict[key] = {"en": new_val, "word_class": None, "gender": None}
            stats["rule_3_1_and_3_2_fixed"] += 1
            continue
            
        if key in phrasal_verbs_fixes:
            new_key, new_val = phrasal_verbs_fixes[key]
            log_change("RULE 3.3", key, value, new_key, new_val)
            cleaned_dict[new_key] = {"en": new_val, "word_class": None, "gender": None}
            stats["rule_3_3_fixed"] += 1
            continue
            
        # Keep intact
        cleaned_dict[key] = {"en": str(value).strip(), "word_class": None, "gender": None}
        
    stats["total_output"] = len(cleaned_dict)
    
    # Write master dictionary
    master_dict = {
        "metadata": {
            "level": "B1",
            "source": "rivstart_b1",
            "total_words": len(cleaned_dict),
            "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        },
        "words": cleaned_dict
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(master_dict, f, ensure_ascii=False, indent=2)
        
    log_file.close()
    
    # Write stats markdown
    with open(stats_path, "w", encoding="utf-8") as f:
        f.write("# Phase 1: Vocabulary Cleaning Statistics\n\n")
        f.write(f"- **Total Input Words**: {stats['total_input']}\n")
        f.write(f"- **Rule 3.1 & 3.2 (Soft Hyphens & Grammar Fixes)**: {stats['rule_3_1_and_3_2_fixed']} words repaired manually by LLM.\n")
        f.write(f"- **Rule 3.3 (Phrasal Verbs Merged)**: {stats['rule_3_3_fixed']} words merged.\n")
        f.write(f"- **Rule 3.4 (PDF Fragments Deleted)**: {stats['rule_3_4_deleted']} orphan fragments removed.\n")
        f.write(f"- **Total Output Words**: {stats['total_output']}\n")
        
    print(f"Phase 1 complete. Master dictionary generated with {stats['total_output']} words.")

if __name__ == "__main__":
    main()
