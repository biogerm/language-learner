import json

def main():
    with open("../phase1/master_dictionary.json", "r", encoding="utf-8") as f:
        master_dict = json.load(f)
        
    for w in ["eyes,", "freedom", "have", "minded", "ntally", "write"]:
        print(f"'{w}' in keys: {w in master_dict}")
if __name__ == "__main__":
    main()
