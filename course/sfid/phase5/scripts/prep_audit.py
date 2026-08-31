import json
import os

base_dir = "course/sfid/phase2"
audit_file = os.path.join(base_dir, "position_audit_failed.json")
output_file = os.path.join(base_dir, "position_audit_prep.md")

with open(audit_file, 'r', encoding='utf-8') as f:
    items = json.load(f)

md_content = "# Audit Items\n\n"

for i, item in enumerate(items):
    art_id = item['article_id']
    sent_id = item['sentence_id']
    
    # fetch english text
    art_path = os.path.join(base_dir, "articles_translated", f"{art_id.replace('art_', 'art_')}.json")
    en_text = "N/A"
    with open(art_path, 'r', encoding='utf-8') as f:
        art_data = json.load(f)
        for s in art_data['sentences']:
            if s['sentence_id'] == sent_id:
                en_text = s.get('en', 'N/A')
                break
                
    md_content += f"## Item {i}\n"
    md_content += f"- **Location**: {art_id} -> {sent_id} ({item['word_type']})\n"
    md_content += f"- **Target Base Form**: {item['base_form']}\n"
    md_content += f"- **LLM Extracted Word**: {item['word_in_sentence']}\n"
    md_content += f"- **Matches Found**: {item['matches_found']}\n"
    md_content += f"- **SV**: {item['sv_text']}\n"
    md_content += f"- **EN**: {en_text}\n"
    md_content += "\n"

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(md_content)
    
print(f"Prep file saved to {output_file}")
