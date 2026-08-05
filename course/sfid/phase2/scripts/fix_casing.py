import json

def fix_casing(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for art_id, sentences in data.items():
        for s in sentences:
            sv = s['sv']
            for w_type in ['target_words', 'secondary_words']:
                if w_type in s:
                    for w in s[w_type]:
                        start = w.get('position_start')
                        end = w.get('position_end')
                        if start is not None and end is not None:
                            extracted = sv[start:end]
                            if extracted != w['word_in_sentence']:
                                w['word_in_sentence'] = extracted
                                
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    fix_casing("enrich_out_2.json")
