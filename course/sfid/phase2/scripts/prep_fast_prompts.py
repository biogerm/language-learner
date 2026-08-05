import json
import glob
import os

def prep():
    files = sorted(glob.glob("articles_translated/art_*.json"))
    batch_size = 19
    
    for i in range(0, len(files), batch_size):
        batch_files = files[i:i+batch_size]
        batch_idx = (i // batch_size) + 1
        
        prompt_content = f"--- BATCH {batch_idx} ---\n\n"
        prompt_content += "Your task is to provide contextual_en translations for target_words and pick 2-3 secondary_words per sentence.\n"
        prompt_content += "Output a SINGLE JSON object exactly like this format. Do NOT wrap it in markdown block, or if you do, ensure it's valid JSON:\n"
        prompt_content += "{\n  \"art_00_s001\": {\n    \"target_words\": {\"sv_word1\": \"en_translation\", \"sv_word2\": \"en_translation\"},\n"
        prompt_content += "    \"secondary_words\": {\"sv_challenging_word1\": \"en_translation\", \"sv_challenging_word2\": \"en_translation\"}\n  }\n}\n\n"
        
        for filepath in batch_files:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            for s in data["sentences"]:
                sid = s['sentence_id']
                prompt_content += f"[{sid}]\n"
                prompt_content += f"sv: {s['sv']}\n"
                prompt_content += f"en: {s['en']}\n"
                tw_list = [w['word_in_sentence'] for w in s.get('target_words', [])]
                if tw_list:
                    prompt_content += "target_words_to_translate: " + ", ".join(tw_list) + "\n"
                prompt_content += "\n"
                
        with open(f"prompts/fast_batch_{batch_idx}.txt", "w", encoding="utf-8") as f:
            f.write(prompt_content)
            
    print(f"Generated {(len(files)-1) // batch_size + 1} fast batch prompts.")

if __name__ == "__main__":
    os.makedirs("prompts", exist_ok=True)
    prep()
