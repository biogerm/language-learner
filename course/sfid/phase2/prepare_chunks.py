import json
import os
import math

def main():
    os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
    input_path = "../phase1/master_dictionary.json"
    
    with open(input_path, "r", encoding="utf-8") as f:
        master_dict = json.load(f)
        
    words = master_dict["words"]
    word_list = [{"sv": k, "en": v["en"]} for k, v in words.items()]
    
    num_chunks = 3
    chunk_size = math.ceil(len(word_list) / num_chunks)
    
    for i in range(num_chunks):
        chunk = word_list[i*chunk_size : (i+1)*chunk_size]
        out_path = f"chunk_{i+1}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(chunk, f, ensure_ascii=False, indent=2)
        print(f"Created {out_path} with {len(chunk)} words.")

if __name__ == "__main__":
    main()
