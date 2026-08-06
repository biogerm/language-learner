import json, os, time
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-pro")

with open("course/sfid/phase2/articles_translated/art_19.json", "r") as f:
    art = json.load(f)

print("Starting LLM extraction for contextual translations...")
modified = False

for s in art.get("sentences", []):
    sv_text = s.get("sv")
    en_text = s.get("en")
    target_words = s.get("target_words", [])
    
    if not target_words: continue
    
    prompt = f"""
You are an expert Swedish-English translator.
I have a Swedish sentence and its English translation.
Swedish: "{sv_text}"
English: "{en_text}"

The following Swedish target words are present in the Swedish sentence. For each target word, find its EXACT contextual translation in the English sentence. It MUST be a substring from the English sentence if possible, or a direct translation of how it functions in this specific sentence context.

Target Words:
"""
    for w in target_words:
        prompt += f"- {w.get('word_in_sentence')} (base form: {w.get('base_form')})\n"
        
    prompt += """
Return a pure JSON list of objects, each containing:
"base_form": the base form of the word
"contextual_en": the exact English translation used in this context.
No markdown block, just the JSON list.
"""
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"): text = text[7:]
        if text.endswith("```"): text = text[:-3]
        results = json.loads(text.strip())
        
        for w in target_words:
            for r in results:
                if r.get("base_form") == w.get("base_form"):
                    w["contextual_en"] = r.get("contextual_en")
                    modified = True
    except Exception as e:
        print(f"Error on sentence {s.get('sentence_id')}: {e}")
        
    time.sleep(1) # rate limiting

if modified:
    with open("course/sfid/phase2/articles_translated/art_19.json", "w", encoding="utf-8") as f:
        json.dump(art, f, ensure_ascii=False, indent=4)
        
    # Sync back to un-translated
    untrans = json.loads(json.dumps(art))
    untrans["article_id"] = untrans["article_id"].replace("art_", "article_")
    for s in untrans.get("sentences", []):
        s["en"] = ""
        for tw in s.get("target_words", []):
            tw.pop("contextual_en", None)
        for sw in s.get("secondary_words", []):
            sw.pop("contextual_en", None)
            
    untrans_file = "course/sfid/phase2/articles/article_19.json"
    with open(untrans_file, "w", encoding="utf-8") as f:
        json.dump(untrans, f, ensure_ascii=False, indent=4)
        
    print("Done! Updated art_19.json with accurate contextual translations.")
