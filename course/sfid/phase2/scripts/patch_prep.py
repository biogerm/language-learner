import json

def prep():
    with open("injection_errors.log", "r") as f:
        lines = f.readlines()
        
    sids = set()
    for line in lines:
        if line.startswith("[art_"):
            sid = line.split("]")[0][1:]
            sids.add(sid)
            
    prompt = "You need to fix missing translations for the following sentences. Please provide the contextual_en mapping for target_words and a few secondary_words.\n\n"
    
    import glob
    files = glob.glob("articles_translated/art_*.json")
    for filepath in files:
        with open(filepath, "r") as f:
            data = json.load(f)
        for s in data["sentences"]:
            if s["sentence_id"] in sids:
                prompt += f"[{s['sentence_id']}]\n"
                prompt += f"sv: {s['sv']}\n"
                prompt += f"en: {s['en']}\n"
                tw = [w['word_in_sentence'] for w in s.get('target_words', []) if not w.get("contextual_en")]
                if tw:
                    prompt += "target_words_to_translate: " + ", ".join(tw) + "\n"
                prompt += "\n"
                
    with open("prompts/patch_prompt.txt", "w") as f:
        f.write(prompt)
    print(f"Prepared patch prompt for {len(sids)} sentences.")

if __name__ == "__main__":
    prep()
