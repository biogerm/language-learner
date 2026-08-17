import os
import json
import re

def process_articles():
    base_dir = "/Users/qin.an/hm.com/Developer/antigravity/Language learner/course/sfid/phase2"
    translated_dir = os.path.join(base_dir, "articles_translated")
    articles_dir = os.path.join(base_dir, "articles")
    
    # Correct base_dir to actual
    base_dir = "./course/sfid/phase2"
    translated_dir = os.path.join(base_dir, "articles_translated")
    articles_dir = os.path.join(base_dir, "articles")
    
    audit_failed = []
    
    # Swedish letter boundaries
    # Using negative lookbehind and lookahead for [a-zA-ZåäöÅÄÖéÉüÜ]
    boundary_pattern = r"(?<![a-zA-ZåäöÅÄÖéÉüÜ]){}(?![a-zA-ZåäöÅÄÖéÉüÜ])"

    for i in range(58):
        filename = f"art_{i:02d}.json"
        trans_filepath = os.path.join(translated_dir, filename)
        art_filepath = os.path.join(articles_dir, f"article_{i:02d}.json")
        
        if not os.path.exists(trans_filepath):
            continue
            
        with open(trans_filepath, 'r', encoding='utf-8') as f:
            trans_data = json.load(f)
            
        has_changes = False
        
        for sentence in trans_data.get('sentences', []):
            sv_text = sentence.get('sv', '')
            
            for word_type in ['target_words', 'secondary_words']:
                for word_entry in sentence.get(word_type, []):
                    word_in_sentence = word_entry.get('word_in_sentence', '')
                    
                    if not word_in_sentence:
                        continue
                        
                    # Escape the word for regex
                    escaped_word = re.escape(word_in_sentence)
                    pattern = boundary_pattern.format(escaped_word)
                    
                    try:
                        # Find all matches (case insensitive)
                        matches = list(re.finditer(pattern, sv_text, re.IGNORECASE))
                    except re.error as e:
                        matches = []
                        
                    if len(matches) == 1:
                        # Perfect match! Update positions.
                        match = matches[0]
                        new_start = match.start()
                        new_end = match.end()
                        
                        if word_entry.get('position_start') != new_start or word_entry.get('position_end') != new_end:
                            word_entry['position_start'] = new_start
                            word_entry['position_end'] = new_end
                            has_changes = True
                    else:
                        # 0 matches (mismatch/parasite) or >1 match (duplicates)
                        audit_failed.append({
                            'article_id': trans_data.get('article_id'),
                            'sentence_id': sentence.get('sentence_id'),
                            'sv_text': sv_text,
                            'word_type': word_type,
                            'base_form': word_entry.get('base_form'),
                            'word_in_sentence': word_in_sentence,
                            'matches_found': len(matches),
                            'old_position_start': word_entry.get('position_start'),
                            'old_position_end': word_entry.get('position_end')
                        })
                        
        if has_changes:
            # Save translated version
            with open(trans_filepath, 'w', encoding='utf-8') as f:
                json.dump(trans_data, f, ensure_ascii=False, indent=2)
                
            # Keep articles version in sync (copy sv and target_words)
            if os.path.exists(art_filepath):
                with open(art_filepath, 'r', encoding='utf-8') as f:
                    art_data = json.load(f)
                    
                # Create a lookup from trans_data
                trans_sentences = {s['sentence_id']: s for s in trans_data.get('sentences', [])}
                art_changed = False
                
                for art_sent in art_data.get('sentences', []):
                    sid = art_sent.get('sentence_id')
                    if sid in trans_sentences:
                        ts = trans_sentences[sid]
                        if 'target_words' in ts:
                            art_sent['target_words'] = ts['target_words']
                            art_changed = True
                            
                if art_changed:
                    with open(art_filepath, 'w', encoding='utf-8') as f:
                        json.dump(art_data, f, ensure_ascii=False, indent=2)

    # Save the audit report
    report_path = os.path.join(os.path.dirname(translated_dir), 'position_audit_failed.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(audit_failed, f, ensure_ascii=False, indent=2)
        
    print(f"Recalibration complete. Found {len(audit_failed)} problematic word positions.")
    print(f"Audit report saved to: {report_path}")

if __name__ == '__main__':
    process_articles()
