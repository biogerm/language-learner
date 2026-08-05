import json

def check(w, data):
    if w in data:
        print(f"'{w}' EXISTS in master_dictionary.json")
    else:
        print(f"'{w}' DOES NOT exist in master_dictionary.json")

def main():
    with open("../phase1/master_dictionary.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    check("frihet", data)
    check("öppensinnad", data)
    check("mentalt", data)
    check("ha", data)
    check("blunda", data)
    check("write", data)

if __name__ == "__main__":
    main()
