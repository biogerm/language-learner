import json

def main():
    with open("../phase1/master_dictionary.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for k, v in data.items():
        if "book" in k.lower() or "climate" in k.lower() or "modern freedom" in k.lower() or "open-minded" in k.lower() or "i have a dream" in k.lower() or "ntally" in k.lower():
            print(f"Key: {k}, Value: {v}")

if __name__ == "__main__":
    main()
