import json
import random
import os
import math

def main():
    os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
    
    with open("clustered_dictionary.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    abstract_words = data["Abstrakta Koncept"]
    specific_themes = [k for k in data.keys() if k != "Abstrakta Koncept"]
    
    batches = []
    
    # Shuffle abstract words (with fixed seed for reproducibility)
    random.seed(42)
    random.shuffle(abstract_words)
    
    abs_index = 0
    
    for theme in specific_themes:
        words_in_theme = data[theme]
        random.shuffle(words_in_theme)
        
        # Split specific words into chunks of 18
        chunk_size = 18
        for i in range(0, len(words_in_theme), chunk_size):
            spec_chunk = words_in_theme[i:i+chunk_size]
            
            # Pull 32 abstract words
            abs_chunk = abstract_words[abs_index:abs_index+32]
            abs_index += 32
            
            batches.append({
                "theme": theme,
                "target_words": spec_chunk + abs_chunk,
                "word_count": len(spec_chunk) + len(abs_chunk)
            })
            
    # If any abstract words are left over, group them into a final mixed batch
    remaining_abstract = abstract_words[abs_index:]
    if remaining_abstract:
        for i in range(0, len(remaining_abstract), 50):
            chunk = remaining_abstract[i:i+50]
            batches.append({
                "theme": "Blandade Ämnen (Mixed Topics)",
                "target_words": chunk,
                "word_count": len(chunk)
            })
            
    # Split the resulting article prompt batches among the 3 subagents
    num_subagents = 3
    batches_per_agent = math.ceil(len(batches) / num_subagents)
    
    for i in range(num_subagents):
        agent_batches = batches[i*batches_per_agent : (i+1)*batches_per_agent]
        with open(f"subagent_tasks_{i+1}.json", "w", encoding="utf-8") as f:
            json.dump(agent_batches, f, ensure_ascii=False, indent=2)
            
    print(f"Total articles planned: {len(batches)}")
    print("Pre-allocation successful! Partitioned into 3 subagent task files without any overlap.")

if __name__ == "__main__":
    main()
