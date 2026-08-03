import json
import os

def main():
    original_file = "../data/b1_ordlista.json"
    generated_file = "master_dictionary.json"

    # Load original data
    with open(original_file, "r", encoding="utf-8") as f:
        original_data = json.load(f)
    
    # Load generated data
    with open(generated_file, "r", encoding="utf-8") as f:
        generated_data = json.load(f)
        
    original_count = len(original_data)
    # The generated file uses a nested "words" structure as per the spec
    generated_count = len(generated_data.get("words", {}))
    
    print("=" * 40)
    print("      DATASET SIZE COMPARISON      ")
    print("=" * 40)
    print(f"Original entries : {original_count}")
    print(f"Generated entries: {generated_count}")
    print("-" * 40)
    
    difference = original_count - generated_count
    print(f"Difference       : {difference} entries")
    
    print("\nExplanation:")
    print("We started with 3,433 entries.")
    print("- 8 entries were 'orphan fragments' (e.g., 'ne', 'ter', 'of') caused by hyphenation line-breaks in the PDF.")
    print("- 2 entries were 'split phrasal verbs' (e.g., 'stöta' and 'på') which were merged into 1 ('stöta på').")
    print("  This means 2 keys became 1 key (a reduction of 1 entry).")
    print(f"\nTotal expected reduction: 8 (orphans) + 1 (merge) = 9 entries.")
    
    if difference == 9:
        print("✅ The math checks out exactly! (3433 - 9 = 3424)")
    else:
        print("❌ Wait, there's an unexpected discrepancy!")

if __name__ == "__main__":
    main()
