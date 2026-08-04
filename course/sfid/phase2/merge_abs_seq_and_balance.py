import json
import random
import os

def main():
    # Load original clustered dictionary for base concrete words
    with open("clustered_dictionary.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    specific_themes = {k: v for k, v in data.items() if k != "Abstrakta Koncept"}
    
    # Initialize collectors for semantic leaning words and pure glue
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
                    # In case of minor capitalization mismatches, try to find the key
                    matched = False
                    for expected_k in semantic_abs.keys():
                        if expected_k in theme or expected_k.split()[0] in theme:
                            semantic_abs[expected_k].extend(words)
                            matched = True
                            break
                    if not matched:
                        # Fallback just put it in glue
                        pure_glue.extend(words)
                        
    # Now we have all concrete words, semantically assigned abstract words, and pure glue.
    # Calculate target capacities to maintain uniform ratio
    total_concrete = sum(len(v) for v in specific_themes.values())
    total_abstract = sum(len(v) for v in semantic_abs.values()) + len(pure_glue)
    ratio = total_abstract / total_concrete
    
    targets = {}
    for theme in specific_themes:
        targets[theme] = {
            "concrete": specific_themes[theme],
            "semantic_abs": semantic_abs[theme],
            "target_abstract": round(len(specific_themes[theme]) * ratio),
            "allocated_glue": []
        }
        
    # Distribute pure glue to meet targets
    random.seed(42)
    random.shuffle(pure_glue)
    
    for theme in targets:
        needed = targets[theme]["target_abstract"] - len(targets[theme]["semantic_abs"])
        if needed > 0 and len(pure_glue) > 0:
            chunk = pure_glue[:needed]
            pure_glue = pure_glue[needed:]
            targets[theme]["allocated_glue"].extend(chunk)
            
    # Distribute any remaining pure glue evenly
    idx = 0
    theme_keys = list(targets.keys())
    while pure_glue:
        targets[theme_keys[idx % len(theme_keys)]]["allocated_glue"].append(pure_glue.pop(0))
        idx += 1
        
    # Build final dictionary
    final_dict = {}
    stats = []
    
    for theme in targets:
        c = targets[theme]["concrete"]
        sa = targets[theme]["semantic_abs"]
        ga = targets[theme]["allocated_glue"]
        total_abs = len(sa) + len(ga)
        total_words = len(c) + total_abs
        
        final_dict[theme] = c + sa + ga
        
        stats.append({
            "theme": theme,
            "concrete": len(c),
            "semantic": len(sa),
            "glue": len(ga),
            "total_abs": total_abs,
            "ratio": total_abs / len(c) if len(c) > 0 else 0
        })
        
    with open("final_semantic_dictionary.json", "w", encoding="utf-8") as f:
        json.dump(final_dict, f, ensure_ascii=False, indent=2)
        
    # Print statistics
    print(f"{'Theme':<25} | {'Concrete':<8} | {'Semantic':<8} | {'Glue':<8} | {'Total Abs':<9} | {'Ratio':<5}")
    print("-" * 75)
    for s in sorted(stats, key=lambda x: x['concrete'], reverse=True):
        print(f"{s['theme'][:24]:<25} | {s['concrete']:<8} | {s['semantic']:<8} | {s['glue']:<8} | {s['total_abs']:<9} | {s['ratio']:.2f}")

if __name__ == "__main__":
    main()
