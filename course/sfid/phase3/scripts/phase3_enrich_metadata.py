import os
import json
import time
from typing import Dict, Any, List, Optional
try:
    from google import genai
    from pydantic import BaseModel, Field
except ImportError:
    print("Please install google-genai and pydantic")
    exit(1)

# Pydantic models for structured output
class WordMetadata(BaseModel):
    word_type: str = Field(description="Part of speech, e.g., verb, noun, adjective, adverb, pronoun, preposition, conjunction, interjection, phrase")
    noun_gender: Optional[str] = Field(description="'en' or 'ett' if it is a noun, else null")
    is_regular_verb: Optional[bool] = Field(description="true if regular verb, false if irregular, else null")
    verb_imperativ: Optional[str] = Field(description="imperative form if verb, else null")
    verb_presens: Optional[str] = Field(description="present tense if verb, else null")
    verb_preteritum: Optional[str] = Field(description="past tense if verb, else null")
    verb_supinum: Optional[str] = Field(description="supine form if verb, else null")
    verb_perfekt_particip: Optional[str] = Field(description="past participle if verb, else null")

class BatchResponse(BaseModel):
    metadata: Dict[str, WordMetadata] = Field(description="Map of Swedish word to its metadata")

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # sfid
    dict_path = os.path.join(base_dir, 'phase1', 'master_dictionary.json')
    out_path = os.path.join(base_dir, 'data', 'word_metadata.json')

    with open(dict_path, 'r', encoding='utf-8') as f:
        master_dict = json.load(f)
    
    words_data = master_dict.get('words', {})
    
    # Load cache
    if os.path.exists(out_path):
        with open(out_path, 'r', encoding='utf-8') as f:
            metadata_cache = json.load(f)
    else:
        metadata_cache = {}

    missing_words = [w for w in words_data.keys() if w not in metadata_cache]
    print(f"Total words: {len(words_data)}. Cached: {len(metadata_cache)}. Missing: {len(missing_words)}")

    if not missing_words:
        print("All words enriched.")
        return

    client = genai.Client()
    batch_size = 50
    
    for i in range(0, len(missing_words), batch_size):
        batch = missing_words[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(len(missing_words)-1)//batch_size + 1} ({len(batch)} words)...")
        
        prompt = "Provide linguistic metadata (part of speech, noun gender, verb conjugations) for the following Swedish words. If a word can be multiple things, pick the most common one. Ensure keys match the requested words exactly.\n\nWords:\n" + "\n".join(f"- {w}" for w in batch)
        
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': BatchResponse,
                }
            )
            
            result = json.loads(response.text)
            metadata = result.get('metadata', {})
            
            for w in batch:
                if w in metadata:
                    metadata_cache[w] = metadata[w]
                else:
                    # fallback
                    metadata_cache[w] = {
                        "word_type": "unknown",
                        "noun_gender": None,
                        "is_regular_verb": None,
                        "verb_imperativ": None,
                        "verb_presens": None,
                        "verb_preteritum": None,
                        "verb_supinum": None,
                        "verb_perfekt_particip": None
                    }
                    
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(metadata_cache, f, indent=2, ensure_ascii=False)
                
            time.sleep(1) # simple rate limit
            
        except Exception as e:
            print(f"Error on batch {i}: {e}")
            break

if __name__ == '__main__':
    main()
