import json

def main():
    words_to_check = [
        "Hur många?", "Varför", "Skulle det inte vara bättre att?", 
        "en och en halv", "faktisk", "handla med", "högsta dröm",
        "i mitten av", "kombinera", "komma tillbaka", "lika många",
        "lämplig", "plocka", "respektive", "sitta", "tioårsåldern", "toppa"
    ]
    
    with open("sfid_phase2_articles.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    all_used = set()
    for stage in data.get("stages", []):
        for art in stage.get("articles", []):
            for t in art.get("target_words", []):
                all_used.add(t["base_form"])
                
    for w in words_to_check:
        if w in all_used:
            print(f"{w} IS in target_words.")
        else:
            print(f"{w} is MISSING from target_words.")
            
    # Are they in the sv text?
    sv_text_combined = ""
    for stage in data.get("stages", []):
        for art in stage.get("articles", []):
            if "sentences" in art:
                for s in art["sentences"]:
                    sv_text_combined += s.get("sv", "") + " "
                    
    for w in words_to_check:
        if w.lower() in sv_text_combined.lower():
            print(f"'{w}' is in the actual text (untracked).")

if __name__ == "__main__":
    main()
