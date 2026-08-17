import json
import re
import glob

def extract_word_at_pos(sv, pos):
    # Find word at pos
    match = re.search(r'[a-zA-ZåäöÅÄÖ\-]+', sv[pos:])
    if match and match.start() == 0:
        return match.group(0)
    
    # Try finding the first word in that vicinity if there's a space or something
    match = re.search(r'[a-zA-ZåäöÅÄÖ\-]+', sv[pos-2:])
    if match:
        return match.group(0)
        
    return None

def process():
    with open('position_audit_prep.md', 'r') as f:
        content = f.read()

    items = content.split('## Item')[1:]
    fixes = {}
    
    files = glob.glob('./course/sfid/phase2/articles_translated/*.json')
    data_dict = {}
    for f in files:
        with open(f, 'r') as fp:
            data = json.load(fp)
            data_dict[f.split('/')[-1]] = data

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
        s_obj = [s for s in data['sentences'] if s['sentence_id'] == sentence_id][0]
        word_obj = [w for w in s_obj.get(word_type, []) if w['base_form'] == base_form and w['word_in_sentence'] == llm_word][0]
        
        pos = word_obj['position_start']
        sv = s_obj['sv']
        
        extracted = extract_word_at_pos(sv, pos)
        if matches == 0:
            if base_form.lower() not in extracted.lower() and extracted.lower() not in base_form.lower():
                print(f"Mismatch: {base_form} != {extracted} (pos {pos}) in {sv}")

process()
