import json
import glob

def run_check():
    with open("./course/sfid/phase1/master_dictionary.json", "r", encoding="utf-8") as f:
        phase1_data = json.load(f)
    phase1_bases = set(phase1_data.get("words", {}).keys())

    article_files = glob.glob("./course/sfid/phase2/articles/article_*.json")
    phase2_bases = set()
    
    for file_path in article_files:
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                article_data = json.load(f)
                if isinstance(article_data, dict):
                    for sentence in article_data.get("sentences", []):
                        for target in sentence.get("target_words", []):
                            phase2_bases.add(target.get("base_form"))
                else:
                    print(f"File {file_path} is not a dictionary.")
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    missing_in_phase1 = phase2_bases - phase1_bases
    unused_phase1 = phase1_bases - phase2_bases
    
    print(f"Phase 2 Articles ({len(article_files)} files) used {len(phase2_bases)} unique base forms.")
    print(f"Phase 1 Dictionary has {len(phase1_bases)} unique base forms.")
    
    print(f"\nPhase 2 Articles 中额外多出的 {len(missing_in_phase1)} 个词:")
    for w in sorted(missing_in_phase1):
        print(f"  - {w}")

    print(f"\nPhase 1 字典中丢失的 {len(unused_phase1)} 个词 (没有被 Articles 使用):")
    for w in sorted(unused_phase1):
        print(f"  - {w}")

if __name__ == "__main__":
    run_check()
