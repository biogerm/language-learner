import json
import glob

def main():
    files = sorted(glob.glob("articles/art_*.json"))
    out = {}
    for fpath in files:
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
            # get first two sentences to understand the topic
            sents = data.get("sentences", [])
            text = " ".join([s.get("sv", "") for s in sents[:2]])
            out[data["article_id"]] = text
            
    with open("articles_for_titles.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
