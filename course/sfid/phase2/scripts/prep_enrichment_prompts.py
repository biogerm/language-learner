import json
import glob
import os

def prep():
    files = sorted(glob.glob("articles_translated/art_*.json"))
    batch_size = 10
    
    for i in range(0, len(files), batch_size):
        batch_files = files[i:i+batch_size]
        batch_idx = i // batch_size
        
        prompt_content = f"--- BATCH {batch_idx} ---\n\n"
        for filepath in batch_files:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            prompt_content += f"Article ID: {data['article_id']}\n"
            for s in data["sentences"]:
                prompt_content += f"Sentence ID: {s['sentence_id']}\n"
                prompt_content += f"Swedish: {s['sv']}\n"
                prompt_content += f"English: {s['en']}\n"
                prompt_content += "Target words: " + ", ".join([w['word_in_sentence'] for w in s.get('target_words', [])]) + "\n\n"
                
        with open(f"prompts/enrich_batch_{batch_idx}.txt", "w", encoding="utf-8") as f:
            f.write(prompt_content)
            
    print(f"Generated {len(files) // batch_size + 1} batch prompts.")

if __name__ == "__main__":
    os.makedirs("prompts", exist_ok=True)
    prep()
