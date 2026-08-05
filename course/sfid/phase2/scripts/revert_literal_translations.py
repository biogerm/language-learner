import json

def main():
    revert_ids = [
        "art_05_s002", "art_05_s026", "art_06_s015", "art_06_s027", 
        "art_06_s028", "art_06_s029", "art_07_s023", "art_42_s013", 
        "art_45_s021", "art_45_s023", "art_48_s003", "art_34_s006", 
        "art_34_s007", "art_50_s028", "art_51_s033", "art_53_s009", 
        "art_54_s011", "art_54_s014", "art_40_s026", "art_02_s009", 
        "art_02_s014", "art_02_s018", "art_02_s026", "art_03_s011", 
        "art_03_s019", "art_04_s002", "art_04_s009", "art_04_s019", 
        "art_14_s020", "art_00_s002", "art_00_s023", "art_00_s026", 
        "art_01_s015", "art_01_s019", "art_01_s027"
    ]
    
    raw_en_map = {}
    with open("./reports/0c739c98-fc9c-414d-8f46-f329cd4d61c9/teacher_review_modifications_report.md", "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    current_id = None
    for line in lines:
        line = line.strip()
        if line.startswith("### "):
            current_id = line.replace("### ", "")
        elif line.startswith("- **Raw EN**: "):
            if current_id in revert_ids:
                raw_en_text = line.replace("- **Raw EN**: ", "")
                raw_en_map[current_id] = raw_en_text
                
    with open("sfid_phase2_articles_translated.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    reverted_count = 0
    for stage in data.get("stages", []):
        for article in stage.get("articles", []):
            for sentence in article.get("sentences", []):
                s_id = sentence["sentence_id"]
                if s_id in raw_en_map:
                    sentence["en"] = raw_en_map[s_id]
                    reverted_count += 1
                    
    with open("sfid_phase2_articles_translated.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    print(f"Successfully reverted {reverted_count} sentences to their literal Raw EN translation.")

if __name__ == "__main__":
    main()
