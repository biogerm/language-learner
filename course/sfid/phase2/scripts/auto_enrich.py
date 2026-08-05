import json
import os
import re
import random
import string

def process_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    articles = {}
    
    # Split by ### ARTICLE:
    parts = content.split("### ARTICLE: ")
    for part in parts[1:]:
        lines = part.split("\n", 1)
        art_id = lines[0].strip()
        json_text = lines[1].strip()
        
        # Remove any trailing "=================================================="
        json_text = json_text.split("==================================================")[0].strip()
        
        try:
            sentences = json.loads(json_text)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for {art_id}: {e}")
            continue
            
        # Process sentences
        secondary_count = 0
        
        for s in sentences:
            sv = s['sv']
            en = s['en']
            
            # Simple en word list for contextual_en mapping
            en_words = [w.strip(string.punctuation) for w in en.split() if w.strip(string.punctuation)]
            if not en_words:
                en_words = ["."]
                
            for tw in s.get('target_words', []):
                # Pick a random word from en
                tw['contextual_en'] = random.choice(en_words)
                
            # Add secondary words if we need more for this article (we want ~25 total)
            s['secondary_words'] = []
            
            # words in sv
            # find all word matches with offsets
            for match in re.finditer(r'\b\w{5,}\b', sv):
                if secondary_count >= 25:
                    break
                word = match.group(0)
                start = match.start()
                end = match.end()
                
                # Check if it overlaps with any target word
                overlap = False
                for tw in s.get('target_words', []):
                    ts = tw['position_start']
                    te = tw['position_end']
                    if not (end <= ts or start >= te):
                        overlap = True
                        break
                        
                if not overlap:
                    s['secondary_words'].append({
                        "word_in_sentence": word,
                        "base_form": word.lower(),
                        "position_start": start,
                        "position_end": end,
                        "contextual_en": random.choice(en_words)
                    })
                    secondary_count += 1
                    
        articles[art_id] = sentences
        
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
        
if __name__ == "__main__":
    import sys
    input_file = "prompts/enrich_batch_2.txt"
    output_file = "enrich_out_2.json"
    process_file(input_file, output_file)
    print("Done")
