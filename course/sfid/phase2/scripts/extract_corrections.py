import os
import glob

def extract():
    files = glob.glob("teacher_review/review_article_*.md")
    files.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))
    
    for file in files:
        article_id = os.path.basename(file).replace("review_", "").replace(".md", "")
        with open(file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        corrections = []
        in_corrections = False
        for line in lines:
            line = line.strip()
            if "Grammatik och Ordförråd" in line:
                in_corrections = True
                continue
            if in_corrections and line.startswith("**Struktur och Flyt:**") or line.startswith("## Struktur och Flyt"):
                break
            if in_corrections and line.startswith("-") or line.startswith("*"):
                corrections.append(line)
                
        if corrections:
            print(f"[{article_id}]")
            for c in corrections:
                print(f"  {c}")

if __name__ == "__main__":
    extract()
