import json
import glob
import os

def main():
    files = glob.glob("articles_translated/*.json")
    fixed_count = 0
    total_removed = 0
    
    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        modified = False
        for sentence in data.get("sentences", []):
            sv_len = len(sentence.get("sv", ""))
            original_targets = sentence.get("target_words", [])
            valid_targets = []
            
            for tw in original_targets:
                # Check for validity:
                # 1. word_in_sentence must not be empty
                # 2. position_start must be >= 0
                # 3. position_start must be < length of Swedish sentence
                if tw.get("word_in_sentence", "") != "" and \
                   tw.get("position_start", -1) >= 0 and \
                   tw.get("position_start", -1) < sv_len:
                    valid_targets.append(tw)
                else:
                    total_removed += 1
                    
            if len(valid_targets) != len(original_targets):
                sentence["target_words"] = valid_targets
                modified = True
                
        if modified:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            fixed_count += 1
            
    print(f"Fixed {fixed_count} files. Removed {total_removed} invalid ghost target words.")

if __name__ == "__main__":
    main()
