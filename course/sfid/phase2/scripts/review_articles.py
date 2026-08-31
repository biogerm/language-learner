import json
import os
import glob
from google import genai

def main():
    client = genai.Client()
    base_dir = "course/sfid/phase2"
    review_dir = os.path.join(base_dir, "teacher_review")
    
    if not os.path.exists(review_dir):
        os.makedirs(review_dir)
        
    article_files = glob.glob(os.path.join(base_dir, "article_*.json"))
    
    prompt_template = """Du är en professionell SFI-lärare (Svenska för invandrare) som undervisar på D-nivå.
Vänligen läs och rätta följande text. Bedöm den utifrån SFI D-nivåns betygskriterier (grammatik, ordförråd, textstruktur och sammanhang).
Ge en kort, professionell recension som innehåller:
1. Helhetsintryck
2. Grammatik och Ordförråd (Rättelser och förslag)
3. Struktur och Flyt
4. Betyg (t.ex. Godkänt, Väl godkänt) eller en rekommendation för att nå nästa nivå.

Svara på svenska.

Text att recensera:
{text}
"""

    for i, file_path in enumerate(article_files):
        print(f"Processing {file_path} ({i+1}/{len(article_files)})...")
        filename = os.path.basename(file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        sv_text = data.get("sv", "")
        if not sv_text:
            print(f"Skipping {filename}: No 'sv' text found.")
            continue
            
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt_template.format(text=sv_text)
            )
            
            review_text = response.text
            output_filename = filename.replace(".json", "_review.md")
            output_path = os.path.join(review_dir, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(review_text)
            print(f"Successfully wrote review to {output_filename}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    main()
