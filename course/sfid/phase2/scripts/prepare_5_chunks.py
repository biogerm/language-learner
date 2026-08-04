import json
import math
import os

def main():
    os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
    
    with open("clustered_dictionary.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    abstract_words_sv = data.get("Abstrakta Koncept", [])
    
    # Load meanings for context
    with open("../phase1/master_dictionary.json", "r", encoding="utf-8") as f:
        master_data = json.load(f)
        sv_to_en = {sv: meta.get("en", "") for sv, meta in master_data["words"].items()}
        
    abstract_words = [{"sv": w, "en": sv_to_en.get(w, "")} for w in abstract_words_sv]
    
    num_chunks = 5
    chunk_size = math.ceil(len(abstract_words) / num_chunks)
    
    for i in range(num_chunks):
        chunk = abstract_words[i*chunk_size : (i+1)*chunk_size]
        with open(f"abs_chunk_seq_{i+1}.json", "w", encoding="utf-8") as f:
            json.dump(chunk, f, ensure_ascii=False, indent=2)
            
    print(f"Total abstract words: {len(abstract_words)}")
    print(f"Partitioned into 5 chunks of ~{chunk_size} words each.")

if __name__ == "__main__":
    main()
