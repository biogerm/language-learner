import os
import json
import math

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # sfid
    dict_path = os.path.join(base_dir, 'phase1', 'master_dictionary.json')
    out_dir = os.path.join(base_dir, 'phase3', 'data', 'chunks')
    
    with open(dict_path, 'r', encoding='utf-8') as f:
        master_dict = json.load(f)
        
    words = list(master_dict.get('words', {}).keys())
    total_words = len(words)
    print(f"Loaded {total_words} words from dictionary.")
    
    # Split into 2 chunks
    chunk_size = math.ceil(total_words / 2)
    chunk1 = words[:chunk_size]
    chunk2 = words[chunk_size:]
    
    with open(os.path.join(out_dir, 'keys_1.json'), 'w', encoding='utf-8') as f:
        json.dump(chunk1, f, ensure_ascii=False)
        
    with open(os.path.join(out_dir, 'keys_2.json'), 'w', encoding='utf-8') as f:
        json.dump(chunk2, f, ensure_ascii=False)
        
    print(f"Wrote {len(chunk1)} words to keys_1.json and {len(chunk2)} words to keys_2.json")

if __name__ == '__main__':
    main()
