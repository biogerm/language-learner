import re
import difflib
import json

def get_best_match(base_form, llm_word, sv, en):
    words = re.findall(r'[a-zA-ZåäöÅÄÖ\-]+', sv)
    
    # 1. Exact match of base_form as substring in a word
    contains = [w for w in words if base_form.lower() in w.lower()]
    if len(contains) == 1:
        return contains[0]
        
    # 2. Starts with base_form
    starts = [w for w in words if w.lower().startswith(base_form.lower())]
    if len(starts) == 1:
        return starts[0]
        
    # 3. difflib
    matches = difflib.get_close_matches(base_form, words, n=1, cutoff=0.3)
    if matches:
        return matches[0]
        
    return llm_word

with open('position_audit_prep.md', 'r') as f:
    content = f.read()

items = content.split('## Item')[1:]
fixes = {}

for item in items:
    lines = item.strip().split('\n')
    idx = lines[0].strip()
    loc = [l for l in lines if l.startswith('- **Location**:')][0].split('**Location**: ')[1].strip()
    file_name = loc.split(' -> ')[0]
    sentence_id = loc.split(' -> ')[1].split(' (')[0]
    word_type = loc.split('(')[1].split(')')[0]
    base_form = [l for l in lines if l.startswith('- **Target Base Form**:')][0].split('**Target Base Form**: ')[1].strip()
    llm_word = [l for l in lines if l.startswith('- **LLM Extracted Word**:')][0].split('**LLM Extracted Word**: ')[1].strip()
    matches = int([l for l in lines if l.startswith('- **Matches Found**:')][0].split('**Matches Found**: ')[1].strip())
    sv = [l for l in lines if l.startswith('- **SV**:')][0].split('**SV**: ')[1].strip()
    en = [l for l in lines if l.startswith('- **EN**:')][0].split('**EN**: ')[1].strip()
    
    target = llm_word
    occurrence = 0
    if matches == 0:
        target = get_best_match(base_form, llm_word, sv, en)
    elif matches > 1:
        target = llm_word
        occurrence = 0
        
    print(f"    '{sentence_id}_{base_form}': {{'word': '{target}', 'occ': {occurrence}}},")
