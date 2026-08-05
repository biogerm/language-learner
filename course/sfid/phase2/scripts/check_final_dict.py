import json

def main():
    with open("final_semantic_dictionary.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for cat, words in data.items():
        for item in words:
            if "book" in item["sv"].lower() or "climate" in item["sv"].lower():
                print(f"Cat: {cat}, Word: {item['sv']}")

if __name__ == "__main__":
    main()
