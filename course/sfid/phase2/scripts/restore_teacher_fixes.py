import json

def main():
    # We want to re-apply the teacher's fixes to these IDs
    # because they involve broken english, weird word order, or grammar issues
    # that shouldn't be preserved.
    revert_ids = [
        "art_05_s002", "art_05_s026", "art_06_s027", 
        "art_45_s021", "art_45_s023", "art_48_s003", 
        "art_50_s028", "art_51_s033", "art_53_s009", 
        "art_40_s026", "art_02_s009", "art_02_s014", "art_02_s018", 
        "art_02_s026", "art_03_s011", "art_03_s019", 
        "art_04_s009", "art_04_s019", "art_14_s020", 
        "art_00_s002", "art_00_s023", "art_00_s026", 
        "art_01_s015", "art_01_s019", "art_01_s027"
    ]
    
    val_en_map = {}
    with open("./reports/teacher_review_modifications_report.md", "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    current_id = None
    for line in lines:
        line = line.strip()
        if line.startswith("### "):
            current_id = line.replace("### ", "")
        elif line.startswith("- **Validated EN**: "):
            if current_id in revert_ids:
                val_en_text = line.replace("- **Validated EN**: ", "")
                val_en_map[current_id] = val_en_text
                
    with open("sfid_phase2_articles_translated.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    restored_count = 0
    for stage in data.get("stages", []):
        for article in stage.get("articles", []):
            for sentence in article.get("sentences", []):
                s_id = sentence["sentence_id"]
                if s_id in val_en_map:
                    sentence["en"] = val_en_map[s_id]
                    restored_count += 1
                    
    with open("sfid_phase2_articles_translated.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    print(f"Successfully restored {restored_count} sentences to Teacher's Validated EN.")

if __name__ == "__main__":
    main()
