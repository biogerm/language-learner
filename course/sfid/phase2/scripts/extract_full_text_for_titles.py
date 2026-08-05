import json
import glob
import os

def main():
    files = sorted(glob.glob("articles/article_*.json"))
    out_lines = []
    
    for f in files:
        if "article_plan.json" in f: continue
        
        with open(f, "r", encoding="utf-8") as file:
            data = json.load(file)
            
        art_id = data.get("article_id")
        full_text = " ".join([s.get("sv", "") for s in data.get("sentences", [])])
        
        out_lines.append(f"### ID: {art_id}")
        out_lines.append(full_text)
        out_lines.append("")
        
    with open("full_texts_for_titles.txt", "w", encoding="utf-8") as out:
        out.write("\n".join(out_lines))
        
    print("Extracted full text for titles.")

if __name__ == "__main__":
    main()
