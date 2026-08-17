import re
import difflib
import json

def get_closest_match(word, sentence):
    # Split keeping punctuation separate is better, but difflib on words is okay
    # Let's try to match words
    words = re.findall(r'[a-zA-ZåäöÅÄÖ\-]+', sentence)
    matches = difflib.get_close_matches(word, words, n=1, cutoff=0.3)
    if matches:
        return matches[0]
    return word

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
    
    # Heuristic fix
    target = llm_word
    occurrence = 0
    if matches == 0:
        target = get_closest_match(base_form, sv)
    elif matches > 1:
        target = llm_word
        occurrence = 0 # Default to first
        
    print(f"    '{sentence_id}_{base_form}': {{'word': '{target}', 'occ': {occurrence}}},")
