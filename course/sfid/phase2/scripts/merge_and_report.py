import json
import glob
import os

def main():
    # 1. Load raw translations
    with open("all_translations_raw.json", "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    # 2. Load teacher validated translations
    teacher_files = glob.glob("teacher_validated_*.json")
    validated_dict = {}
    for t_file in teacher_files:
        with open(t_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            validated_dict.update(data)
            
    # 3. Load full article structure
    with open("sfid_phase2_articles.json", "r", encoding="utf-8") as f:
        articles_data = json.load(f)

    total_sentences = 0
    modified_sentences = 0
    modifications = []
    
    # 4. Update structure in-place and compare
    for stage in articles_data.get("stages", []):
        for article in stage.get("articles", []):
            for sentence in article.get("sentences", []):
                total_sentences += 1
                sent_id = sentence["sentence_id"]
                sv_text = sentence["sv"]
                
                raw_en = raw_data.get(sent_id, "")
                val_en = validated_dict.get(sent_id, raw_en)
                
                if val_en.strip() != raw_en.strip():
                    modified_sentences += 1
                    modifications.append({
                        "id": sent_id,
                        "sv": sv_text,
                        "raw_en": raw_en,
                        "val_en": val_en
                    })
                
                # Update English translation
                sentence["en"] = val_en

    # 5. Save updated JSON
    with open("sfid_phase2_articles_translated.json", "w", encoding="utf-8") as f:
        json.dump(articles_data, f, ensure_ascii=False, indent=4)

    # 6. Generate Markdown Report
    report = f"# SFI Phase 2: Translation and Teacher Validation Report\n\n"
    report += f"## Summary\n"
    report += f"- **Total Sentences Validated**: {total_sentences}\n"
    report += f"- **Sentences Modified by Teacher**: {modified_sentences}\n"
    report += f"- **Modification Rate**: {((modified_sentences/total_sentences)*100 if total_sentences > 0 else 0):.2f}%\n\n"
    
    report += f"## Modification Details\n"
    if modifications:
        for mod in modifications:
            report += f"### {mod['id']}\n"
            report += f"- **SV**: {mod['sv']}\n"
            report += f"- **Raw EN**: {mod['raw_en']}\n"
            report += f"- **Validated EN**: {mod['val_en']}\n\n"
    else:
        report += "No modifications were made. The initial translations were perfect!\n"

    with open("../../teacher_review_modifications_report.md", "w", encoding="utf-8") as f:
        f.write(report)
        
    print(f"Validation complete. Modified {modified_sentences} out of {total_sentences} sentences.")
    print("Saved final data to sfid_phase2_articles_translated.json")

if __name__ == '__main__':
    main()
