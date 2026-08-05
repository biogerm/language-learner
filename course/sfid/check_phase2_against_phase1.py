import json

def run_check():
    # Load Phase 1 Dictionary
    with open("./course/sfid/phase1/master_dictionary.json", "r", encoding="utf-8") as f:
        phase1_data = json.load(f)
    
    phase1_bases = set(phase1_data.get("words", {}).keys())

    # Load Phase 2 Articles
    with open("./course/sfid/phase2/sfid_phase2_articles.json", "r", encoding="utf-8") as f:
        phase2_data = json.load(f)
    
    phase2_bases = set()
    for step in phase2_data.get("stages", phase2_data.get("steps", [])):
        for article in step.get("articles", []):
            for sentence in article.get("sentences", []):
                for target in sentence.get("target_words", []):
                    phase2_bases.add(target.get("base_form"))

    missing_in_phase1 = phase2_bases - phase1_bases
    unused_phase1 = phase1_bases - phase2_bases
    
    print(f"Phase 2 中额外多出的 {len(missing_in_phase1)} 个词（存在于 Phase 2，但不在 Phase 1 字典中）:")
    for w in sorted(missing_in_phase1):
        print(f"  - {w}")

    print(f"\nPhase 1 字典中丢失的 {len(unused_phase1)} 个词（存在于 Phase 1，但完全没被纳入 Phase 2 文章）:")
    for w in sorted(unused_phase1):
        print(f"  - {w}")

if __name__ == "__main__":
    run_check()
