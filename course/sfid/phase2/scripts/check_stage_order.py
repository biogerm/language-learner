import json

def main():
    with open("sfid_phase2_articles.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for stage in data.get("stages", []):
        print(f"{stage['stage_id']}: {stage['stage_title']} (articles: {len(stage['articles'])})")

if __name__ == "__main__":
    main()
