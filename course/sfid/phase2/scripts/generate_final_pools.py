import json
import os

def main():
    # Load original clustered dictionary for base concrete words
    with open("clustered_dictionary.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    specific_themes = {k: v for k, v in data.items() if k != "Abstrakta Koncept"}
    
    semantic_abs = {k: [] for k in specific_themes.keys()}
    pure_glue = []
    
    # Merge the 5 sequential outputs from the Subagent
    for i in range(1, 6):
        filename = f"abs_out_seq_{i}.json"
        if not os.path.exists(filename):
            continue
            
        with open(filename, "r", encoding="utf-8") as f:
            batch_data = json.load(f)
            for theme, words in batch_data.items():
                if theme == "Glue":
                    pure_glue.extend(words)
                elif theme in semantic_abs:
                    semantic_abs[theme].extend(words)
                else:
                    # Match slightly fuzzy keys
                    matched = False
                    for expected_k in semantic_abs.keys():
                        if expected_k in theme or expected_k.split()[0] in theme:
                            semantic_abs[expected_k].extend(words)
                            matched = True
                            break
                    if not matched:
                        pure_glue.extend(words)
                        
    # Build core themes (Concrete + Semantic)
    core_themes = {}
    for theme in specific_themes:
        core_themes[theme] = specific_themes[theme] + semantic_abs[theme]
        
    # Write to files
    with open("core_themes.json", "w", encoding="utf-8") as f:
        json.dump(core_themes, f, ensure_ascii=False, indent=2)
        
    with open("global_glue_pool.json", "w", encoding="utf-8") as f:
        json.dump(pure_glue, f, ensure_ascii=False, indent=2)
        
    print(f"Created core_themes.json with {sum(len(v) for v in core_themes.values())} words.")
    print(f"Created global_glue_pool.json with {len(pure_glue)} words.")

if __name__ == "__main__":
    main()
