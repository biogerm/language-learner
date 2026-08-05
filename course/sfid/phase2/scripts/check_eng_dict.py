import json

def main():
    with open("../phase1/master_dictionary.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for k, v in data.items():
        if k.lower() in ["book", "climate", "modern freedom", "open-minded", "i have a dream", "ntally"]:
            print(f"Key: {k}, Value: {v}")

if __name__ == "__main__":
    main()
