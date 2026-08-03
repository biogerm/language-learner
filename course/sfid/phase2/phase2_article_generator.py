import json
import os
import urllib.request
import time
import uuid

API_KEY = os.environ.get("GEMINI_API_KEY")
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={API_KEY}"

def call_gemini(prompt):
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "response_mime_type": "application/json"
        }
    }
    
    req = urllib.request.Request(API_URL, json.dumps(data).encode('utf-8'), {'Content-Type': 'application/json'})
    
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                text = result['candidates'][0]['content']['parts'][0]['text']
                return json.loads(text)
        except Exception as e:
            print(f"API Error (attempt {attempt+1}): {e}")
            time.sleep(5)
    return None

def main():
    # Make sure the directory exists
    os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)

    with open("../phase1/master_dictionary.json", "r", encoding="utf-8") as f:
        master_dict = json.load(f)
        
    words = list(master_dict["words"].keys())
    
    # Process only the first 2 batches (50 words) to prevent a 30-minute timeout for now.
    # We will process all 3424 words
    batch_size = 25
    batches = [words[i:i + batch_size] for i in range(0, len(words), batch_size)]
    
    final_output = {
        "course_id": "sfid",
        "course_title": "SFI D",
        "steps": []
    }
    
    print(f"Total words to process: {len(words)}")
    print(f"Total batches to generate: {len(batches)}")
    
    for idx, batch in enumerate(batches):
        print(f"Generating article {idx+1}/{len(batches)}...")
        
        target_words_json = json.dumps(batch, ensure_ascii=False)
        
        prompt = f"""
You are an expert Swedish language teacher specializing in CEFR Level B1 (SFI Level D). 
Your task is to write a highly coherent, natural-sounding article in Swedish that seamlessly incorporates a specific list of target vocabulary words.

# WRITING STANDARDS:
1. Target Level: STRICTLY CEFR B1. Use grammatical structures appropriate for this level.
2. Context Clues: Provide enough context so a learner can guess its meaning.
3. Length & Flow: Write between 300-500 words. The article must have a clear beginning, middle, and end. 
4. Sentence Length: Average 10-15 words per sentence.
5. Topic: Identify the most suitable unifying theme for the provided words, and create an engaging story or essay about it. Give the article a meaningful title.

# TARGET VOCABULARY (MUST USE 100%):
{target_words_json}

# CONSTRAINTS & OUTPUT FORMAT:
You must output strictly in JSON format matching the requested schema. Do not wrap in markdown code blocks.
Schema:
{{
  "step_id": "step_01",
  "step_title": "Thematic Title (e.g. Daily Life)",
  "articles": [
    {{
      "article_id": "art_{idx+1}",
      "article_title": "...",
      "target_word_count": {len(batch)},
      "sentences": [
        {{
          "sentence_id": "s1",
          "sv": "...",
          "en": "...",
          "target_words": [
            {{
              "word_in_sentence": "soffpotatis",
              "base_form": "soffpotatis",
              "position_start": 25,
              "position_end": 36
            }}
          ]
        }}
      ],
      "primary_words_used": {target_words_json},
      "secondary_words_used": []
    }}
  ]
}}
"""
        result = call_gemini(prompt)
        if result:
            final_output["steps"].append(result)
            print(f"✅ Batch {idx+1} successful!")
            with open("phase2_articles.json", "w", encoding="utf-8") as f:
                json.dump(final_output, f, ensure_ascii=False, indent=2)
            time.sleep(4)
        else:
            print(f"❌ Batch {idx+1} failed after 3 retries.")
            
    print("Done! Saved all batches to phase2_articles.json")

if __name__ == "__main__":
    main()
