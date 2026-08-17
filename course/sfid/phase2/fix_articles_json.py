import json
import os
import glob

def process():
    base_dir = './course/sfid/phase2/articles_translated'
    articles_dir = './course/sfid/phase2/articles'
    files = glob.glob(os.path.join(base_dir, '*.json'))
    
    for trans_path in files:
        fname = os.path.basename(trans_path)
        # map art_00.json to article_00.json
        art_fname = fname.replace('art_', 'article_')
        art_path = os.path.join(articles_dir, art_fname)
        
        if not os.path.exists(art_path):
            continue
            
        with open(trans_path, 'r') as fp:
            data = json.load(fp)
            
        with open(art_path, 'r') as fp:
            art_data = json.load(fp)
            
        modified = False
        # mirror changes
        for s_trans in data['sentences']:
            s_art = next((s for s in art_data['sentences'] if s['sentence_id'] == s_trans['sentence_id']), None)
            if not s_art: continue
            
            for w_type in ['target_words', 'secondary_words']:
                for w_trans in s_trans.get(w_type, []):
                    w_art_list = [w for w in s_art.get(w_type, []) if w['base_form'] == w_trans['base_form']]
                    if w_art_list:
                        # Find the matching word or first one
                        w_art = w_art_list[0]
                        if (w_art.get('word_in_sentence') != w_trans['word_in_sentence'] or 
                            w_art.get('position_start') != w_trans['position_start'] or 
                            w_art.get('position_end') != w_trans['position_end']):
                            
                            w_art['word_in_sentence'] = w_trans['word_in_sentence']
                            w_art['position_start'] = w_trans['position_start']
                            w_art['position_end'] = w_trans['position_end']
                            modified = True
                        
        if modified:
            with open(art_path, 'w') as fp:
                json.dump(art_data, fp, ensure_ascii=False, indent=4)
                
    print("Successfully updated articles directory.")

process()
