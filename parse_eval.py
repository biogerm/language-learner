import re
import json

with open('./course/sfid/phase2/prompts/eval_prompt.txt', 'r') as f:
    lines = f.readlines()

discrepancies = []
current_item = {}
for line in lines:
    line = line.strip()
    if line.startswith('--- '):
        current_item = {'id': line.strip('- ').strip(), 'words': []}
        discrepancies.append(current_item)
    elif line.startswith('sv: '):
        current_item['sv'] = line[4:]
    elif line.startswith('en: '):
        current_item['en'] = line[4:]
    elif line.startswith('Word: '):
        # Format: Word: lata dagar | contextual_en: lazy days | master_en: days of leisure
        parts = line.split('|')
        if len(parts) == 3:
            word = parts[0].replace('Word:', '').strip()
            ctx_en = parts[1].replace('contextual_en:', '').strip()
            mst_en = parts[2].replace('master_en:', '').strip()
            current_item['words'].append({
                'word': word,
                'ctx_en': ctx_en,
                'mst_en': mst_en
            })

with open('parsed_discrepancies.json', 'w') as f:
    json.dump(discrepancies, f, indent=2)

print(f"Total sentences: {len(discrepancies)}")
total_words = sum(len(d['words']) for d in discrepancies)
print(f"Total words: {total_words}")
