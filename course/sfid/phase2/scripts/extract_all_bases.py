import json

def main():
    with open("sfid_phase2_articles.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    bases = set()
    for step in data.get("steps", []):
        for article in step.get("articles", []):
            for sentence in article.get("sentences", []):
                for target in sentence.get("target_words", []):
                    bases.add(target["base_form"])
                    
    with open("all_bases.txt", "w", encoding="utf-8") as f:
        for b in sorted(bases):
            f.write(f"{b}\n")
            
if __name__ == "__main__":
    main()
