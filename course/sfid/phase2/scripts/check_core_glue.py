import json

def main():
    words_to_check = [
        "Hur många?", "Varför", "Skulle det inte vara bättre att?", 
        "en och en halv", "faktisk", "handla med", "högsta dröm",
        "i mitten av", "kombinera", "komma tillbaka", "lika många",
        "lämplig", "plocka", "respektive", "sitta", "tioårsåldern", "toppa"
    ]
    
    with open("core_themes.json", "r", encoding="utf-8") as f:
        core_data = json.load(f)
    core_set = set()
    for k, v in core_data.items():
        core_set.update(v)
        
    with open("global_glue_pool.json", "r", encoding="utf-8") as f:
        glue_data = json.load(f)
    glue_set = set(glue_data)
    
    for w in words_to_check:
        if w in core_set:
            print(f"'{w}' was a CORE word.")
        elif w in glue_set:
            print(f"'{w}' was a GLUE word.")
        else:
            print(f"'{w}' was NOT FOUND in either pool!?")

if __name__ == "__main__":
    main()
