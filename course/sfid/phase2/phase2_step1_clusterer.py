import json
import os
import urllib.request
import time

API_KEY = os.environ.get("GEMINI_API_KEY")
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={API_KEY}"

THEMES = [
    "Vardagsliv (Daily Life)",
    "Arbetsliv (Work & Career)",
    "Hälsa & Medicin (Health & Medicine)",
    "Natur & Miljö (Nature & Environment)",
    "Samhälle & Politik (Society & Politics)",
    "Kultur & Nöje (Culture & Entertainment)",
    "Relationer & Känslor (Relationships & Emotions)",
    "Vetenskap & Teknik (Science & Technology)",
    "Resor & Transport (Travel & Transport)",
    "Mat & Matlagning (Food & Cooking)",
    "Utbildning (Education)",
    "Abstrakta Koncept (Abstract Concepts)"
]

def call_gemini(prompt):
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json"
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
            error_msg = str(e)
            if hasattr(e, 'read'):
                error_msg += " " + e.read().decode('utf-8', errors='ignore')
            print(f"API Error (attempt {attempt+1}): {error_msg}")
            time.sleep(5)
    return None

def main():
    os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
    
    input_path = "../phase1/master_dictionary.json"
    if not os.path.exists(input_path):
        print(f"Error: Could not find {input_path}")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        master_dict = json.load(f)
        
    words = master_dict["words"]
    # Create list of tuples: (swedish_word, english_translation)
    word_list = [(k, v["en"]) for k, v in words.items()]
    
    batch_size = 100
    batches = [word_list[i:i + batch_size] for i in range(0, len(word_list), batch_size)]
    
    # Structure to hold the clustered words
    clustered_dict = {theme: [] for theme in THEMES}
    
    print(f"Starting Semantic Clustering for {len(word_list)} words in {len(batches)} batches.")
    
    # Process only the first 2 batches (200 words) for a rapid demo verification. 
    # Can be extended to all batches easily.
    batches = batches[:2]
    
    for idx, batch in enumerate(batches):
        print(f"Clustering batch {idx+1}/{len(batches)}...")
        
        batch_json = json.dumps([{"sv": w[0], "en": w[1]} for w in batch], ensure_ascii=False)
        themes_list = "\n".join([f"- {t}" for t in THEMES])
        
        prompt = f"""
You are an expert Swedish linguist. I will provide a list of Swedish vocabulary words and their English translations.
Assign ONE semantic theme to each word from the following strictly predefined list of themes:

{themes_list}

Input Words:
{batch_json}

Return STRICTLY a JSON object where keys are the exact themes from the list above, and values are arrays of the Swedish words assigned to that theme. Do not invent new themes.
"""
        result = call_gemini(prompt)
        if result:
            for theme, assigned_words in result.items():
                if theme in clustered_dict:
                    clustered_dict[theme].extend(assigned_words)
                else:
                    # In case AI slightly alters the theme name, try to match it
                    for valid_theme in THEMES:
                        if valid_theme.startswith(theme.split()[0]):
                            clustered_dict[valid_theme].extend(assigned_words)
                            break
            print(f"✅ Batch {idx+1} clustered successfully!")
            time.sleep(3)
        else:
            print(f"❌ Batch {idx+1} failed.")
            
    # Clean up empty themes
    clustered_dict = {k: v for k, v in clustered_dict.items() if len(v) > 0}
    
    with open("clustered_dictionary.json", "w", encoding="utf-8") as f:
        json.dump(clustered_dict, f, ensure_ascii=False, indent=2)
        
    print("Done! Clustered dictionary saved to clustered_dictionary.json")

if __name__ == "__main__":
    main()
