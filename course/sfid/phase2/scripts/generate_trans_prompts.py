import json, glob

def get_sentences(data):
    if isinstance(data, list):
        article_ref = data[0] if len(data) > 0 else {}
    elif "stages" in data:
        article_ref = data["stages"][0]["articles"][0]
    else:
        article_ref = data
    return article_ref.get("sentences", [])

def main():
    files = sorted(glob.glob("articles/article_*.json"))
    batch_size = 10
    
    for i in range(0, len(files), batch_size):
        batch = files[i:i+batch_size]
        prompt = "Translate the following sentences to English. Return a single flat JSON object { 'sentence_id': 'English translation' }. Do NOT include markdown blocks.\n\n"
        
        for f in batch:
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
            sentences = get_sentences(data)
            for s in sentences:
                prompt += f"{s['sentence_id']}: {s['sv']}\n"
                
        with open(f"trans_prompt_{i//batch_size}.txt", "w", encoding="utf-8") as file:
            file.write(prompt)
            
    print(f"Generated {(len(files)-1)//batch_size + 1} prompt files.")

if __name__ == "__main__":
    main()
