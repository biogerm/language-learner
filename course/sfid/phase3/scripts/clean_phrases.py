import os
import json

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    meta_path = os.path.join(base_dir, 'phase3', 'data', 'word_metadata.json')
    
    with open(meta_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
        
    cleared_count = 0
    for word, props in metadata.items():
        if ' ' in word:  # It's a phrase
            # Clear inflections, maybe keep word_type? The user said "不需要做任何处理" (do no processing).
            # So we set everything to None/null.
            props['noun_gender'] = None
            props['is_regular_verb'] = None
            props['verb_imperativ'] = None
            props['verb_presens'] = None
            props['verb_preteritum'] = None
            props['verb_supinum'] = None
            props['verb_perfekt_particip'] = None
            props['adj_en'] = None
            props['adj_ett'] = None
            props['adj_plural'] = None
            props['adj_komparativ'] = None
            props['adj_superlativ'] = None
            cleared_count += 1
            
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
        
    print(f"Cleared inflections for {cleared_count} phrases/multi-word entries.")

if __name__ == '__main__':
    main()
