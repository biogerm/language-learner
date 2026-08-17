import json
import os
import math

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # sfid
    chunks_dir = os.path.join(base_dir, 'phase3', 'data', 'chunks')
    
    # Load filtered lists
    with open(os.path.join(chunks_dir, 'filter_1.json'), 'r', encoding='utf-8') as f:
        f1 = json.load(f)
    with open(os.path.join(chunks_dir, 'filter_2.json'), 'r', encoding='utf-8') as f:
        f2 = json.load(f)
        
    master_filter = f1 + f2
    total_filtered = len(master_filter)
    print(f"Total words after filtering: {total_filtered}")
    
    # Save master filter list just in case
    with open(os.path.join(chunks_dir, 'master_filter.json'), 'w', encoding='utf-8') as f:
        json.dump(master_filter, f, ensure_ascii=False)
        
    # Chunk into groups of 50
    chunk_size = 50
    num_chunks = math.ceil(total_filtered / chunk_size)
    print(f"Creating {num_chunks} chunks for deep annotation...")
    
    for i in range(num_chunks):
        chunk = master_filter[i*chunk_size:(i+1)*chunk_size]
        with open(os.path.join(chunks_dir, f'deep_chunk_{i}.json'), 'w', encoding='utf-8') as f:
            json.dump(chunk, f, ensure_ascii=False)

    print("Done merging and chunking.")

if __name__ == '__main__':
    main()
