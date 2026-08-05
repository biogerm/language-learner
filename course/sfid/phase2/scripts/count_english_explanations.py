import json
import os
import re

def main():
    # Load all articles
    with open("sfid_phase2_articles.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    count = 0
    examples = []
    
    for step in data.get("steps", []):
        for article in step.get("articles", []):
            for sentence in article.get("sentences", []):
                sv_text = sentence.get("sv", "")
                
                # Check for phrases that look like dictionary explanations
                # e.g., "på engelska", "översättas", "även kallad", "på svenska", "engelska ordet"
                pattern = re.compile(r'(på engelska|engelska ordet|även kallad|översättas till|betyder på engelska|engelskt)', re.IGNORECASE)
                if pattern.search(sv_text):
                    count += 1
                    examples.append(f"Art {article['article_id']}: {sv_text}")
                    
    print(f"Total found: {count}")
    for ex in examples:
        print(ex)

if __name__ == "__main__":
    main()
