import json

def main():
    words_to_check = [
        "Hur många?", "Varför", "Skulle det inte vara bättre att?", 
        "en och en halv", "faktisk", "handla med", "högsta dröm",
        "i mitten av", "kombinera", "komma tillbaka", "lika många",
        "lämplig", "plocka", "respektive", "sitta", "tioårsåldern", "toppa"
    ]
    
    with open("clustered_dictionary.json", "r", encoding="utf-8") as f:
        clustered = json.load(f)
        
    for w in words_to_check:
        found = False
        for k, v in clustered.items():
            if w in v:
                print(f"'{w}' was in {k}")
                found = True
                break
        if not found:
            print(f"'{w}' was NOT in clustered_dictionary.json!")

if __name__ == "__main__":
    main()
