import json
import re
import glob
import os

def find_word_near_pos(sv, pos, base_form):
    # Try to find a word starting exactly at pos or slightly before/after
    
    # First, let's just find all words in the sentence and their spans
    words = []
    for match in re.finditer(r'[a-zA-ZåäöÅÄÖ\-]+', sv):
        words.append({
            'word': match.group(0),
            'start': match.start(),
            'end': match.end()
        })
        
    if not words:
        return None
        
    # Sort words by distance to 'pos'
    # We define distance as min(|word.start - pos|, |word.end - pos|) or 0 if pos is inside
    def dist(w):
        if w['start'] <= pos <= w['end']:
            return 0
        return min(abs(w['start'] - pos), abs(w['end'] - pos))
        
    words.sort(key=dist)
    
    # If the closest word has a very large distance, that's weird but we'll take it
    # We can also prefer a word that shares characters with base_form if distances are equal
    best_words = [w for w in words if dist(w) == dist(words[0])]
    if len(best_words) > 1:
        # Prefer one that has base_form as substring or prefix
        for w in best_words:
            if base_form.lower() in w['word'].lower() or w['word'].lower() in base_form.lower():
                return w
                
    return words[0]

def process():
    with open('position_audit_prep.md', 'r') as f:
        content = f.read()

    items = content.split('## Item ')[1:]
    
    # Load all json files from articles_translated
    base_dir = 'course/sfid/phase2/articles_translated'
    files = glob.glob(os.path.join(base_dir, '*.json'))
    
    data_dict = {}
    for f in files:
        with open(f, 'r') as fp:
            data = json.load(fp)
            data_dict[os.path.basename(f)] = data

    modified_files = set()

    for item in items:
        lines = item.strip().split('\n')
        loc = [l for l in lines if l.startswith('- **Location**:')][0].split('**Location**: ')[1].strip()
        file_name = loc.split(' -> ')[0] + '.json'
        sentence_id = loc.split(' -> ')[1].split(' (')[0]
        word_type = loc.split('(')[1].split(')')[0]
        base_form = [l for l in lines if l.startswith('- **Target Base Form**:')][0].split('**Target Base Form**: ')[1].strip()
        llm_word = [l for l in lines if l.startswith('- **LLM Extracted Word**:')][0].split('**LLM Extracted Word**: ')[1].strip()
        matches = int([l for l in lines if l.startswith('- **Matches Found**:')][0].split('**Matches Found**: ')[1].strip())
        
        data = data_dict[file_name]
        s_obj = next((s for s in data['sentences'] if s['sentence_id'] == sentence_id), None)
        if not s_obj:
            print(f"Could not find sentence {sentence_id}")
            continue
            
        # find the exact word_obj
        # Note: there might be multiple with the same base_form, we find the one matching llm_word
        word_objs = [w for w in s_obj.get(word_type, []) if w['base_form'] == base_form and w['word_in_sentence'] == llm_word]
        if not word_objs:
            # Fallback if llm_word is somehow different
            word_objs = [w for w in s_obj.get(word_type, []) if w['base_form'] == base_form]
            
        if not word_objs:
            print(f"Could not find word {base_form} in {sentence_id}")
            continue
            
        word_obj = word_objs[0] # Just take the first one if multiple
        
        pos = word_obj['position_start']
        sv = s_obj['sv']
        
        if matches == 0:
            # Mismatch: update word_in_sentence, position_start, position_end
            best_word = find_word_near_pos(sv, pos, base_form)
            word_obj['word_in_sentence'] = best_word['word']
            word_obj['position_start'] = best_word['start']
            word_obj['position_end'] = best_word['end']
            modified_files.add(file_name)
        elif matches > 1:
            # Multiple matches: find exact occurrence
            # The word_in_sentence is correct, we just need to find the occurrence closest to pos
            # Actually find_word_near_pos might return a slightly different word if there's punctuation,
            # but we want exactly the llm_word.
            occurrences = []
            for match in re.finditer(re.escape(llm_word), sv, re.IGNORECASE):
                occurrences.append({
                    'word': sv[match.start():match.end()],
                    'start': match.start(),
                    'end': match.end()
                })
            if not occurrences:
                print(f"Wait, no occurrences for {llm_word} in {sentence_id}?")
                continue
                
            def dist2(w):
                if w['start'] <= pos <= w['end']:
                    return 0
                return min(abs(w['start'] - pos), abs(w['end'] - pos))
                
            occurrences.sort(key=dist2)
            best_occ = occurrences[0]
            
            # Update position_start and position_end
            word_obj['word_in_sentence'] = best_occ['word']
            word_obj['position_start'] = best_occ['start']
            word_obj['position_end'] = best_occ['end']
            modified_files.add(file_name)

    # Now write the files back to both articles_translated and articles directories
    articles_dir = 'course/sfid/phase2/articles'
    
    for fname in modified_files:
        data = data_dict[fname]
        
        # Write to articles_translated
        trans_path = os.path.join(base_dir, fname)
        with open(trans_path, 'w') as fp:
            json.dump(data, fp, ensure_ascii=False, indent=4)
            
        # Write to articles (these might not have 'en' and 'contextual_en', but we can just overwrite them or update only positions)
        # Wait, the instruction says: "overwrite these values in the JSON files. Your script must process all 174 items and update art_*.json in both articles_translated and articles directories."
        # The articles directory has its own JSON files, probably without translations. We should modify them carefully.
        art_path = os.path.join(articles_dir, fname)
        if os.path.exists(art_path):
            with open(art_path, 'r') as fp:
                art_data = json.load(fp)
                
            # mirror changes
            for s_trans in data['sentences']:
                s_art = next((s for s in art_data['sentences'] if s['sentence_id'] == s_trans['sentence_id']), None)
                if not s_art: continue
                
                for w_type in ['target_words', 'secondary_words']:
                    for w_trans in s_trans.get(w_type, []):
                        w_art_list = [w for w in s_art.get(w_type, []) if w['base_form'] == w_trans['base_form']]
                        if w_art_list:
                            # Update the first matching one
                            w_art_list[0]['word_in_sentence'] = w_trans['word_in_sentence']
                            w_art_list[0]['position_start'] = w_trans['position_start']
                            w_art_list[0]['position_end'] = w_trans['position_end']
                            
            with open(art_path, 'w') as fp:
                json.dump(art_data, fp, ensure_ascii=False, indent=4)

    print(f"Successfully processed {len(modified_files)} files.")

process()
