import os
import json
import glob

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # sfid
    chunks_dir = os.path.join(base_dir, 'phase3', 'data', 'chunks')
    out_path = os.path.join(base_dir, 'phase3', 'data', 'word_metadata.json')
    
    meta_files = glob.glob(os.path.join(chunks_dir, 'meta_chunk_*.json'))
    merged_metadata = {}
    
    for mf in meta_files:
        try:
            with open(mf, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Ensure the data is a dictionary mapping word to metadata, or list of dicts.
                # In my prompt I said: "The JSON must follow this structure for each word: ..."
                # Usually they return a JSON object with words as keys or a list. Let's inspect.
                # Actually, I didn't explicitly say mapping. Let's check how they output it.
                if isinstance(data, dict):
                    # They might have returned {"metadata": {...}} or direct mapping
                    if "metadata" in data:
                        merged_metadata.update(data["metadata"])
                    else:
                        merged_metadata.update(data)
                elif isinstance(data, list):
                    # If they returned a list, I hope they included the word!
                    for item in data:
                        if 'word' in item:
                            merged_metadata[item['word']] = item
        except Exception as e:
            print(f"Failed to load {mf}: {e}")
            
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(merged_metadata, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully merged {len(merged_metadata)} words into word_metadata.json.")

if __name__ == '__main__':
    main()
