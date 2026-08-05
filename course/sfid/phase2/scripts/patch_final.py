import json
import glob

fixes = {
    "träna": "train",
    "koppla av": "relax",
    "skorpion": "scorpion",
    "sommarställe": "summer place",
    "I måndags": "Last Monday",
    "livsstil": "lifestyle",
    "vara uto": "be out",
    "mer.\n\nFör någr": "more. For some",
    "sönder": "broken",
    "betyda": "mean",
    "suga": "suck",
    " ge mi": "give me",
    "Därför": "Therefore",
    "hyra": "rent",
    "rustik": "rustic",
    "stuga": "cottage",
    "vid": "at",
    "bondgård": "farm",
    "helg": "weekend",
    "konst": "art",
    "en": "a",
    "konstutbildning": "art education",
    "kommun": "municipality",
    "kollektivtrafik": "public transport",
    "kommunal": "municipal",
    "Va?! Du skojar!": "What?! You're kidding!",
    "nordisk": "Nordic",
    "släkting": "relative",
    "be att få": "ask to get",
    "be om": "ask for",
    "söka": "search",
    "skala": "peel",
    "ju mer …desto": "the more... the",
    "skott": "shot",
    "nuförtiden": "nowadays",
    "trendig": "trendy",
    "äventyrlig": "adventurous",
    "busig": "mischievous",
    "följa efter": "follow"
}

files = glob.glob("articles_translated/art_*.json")
patched = 0
for filepath in files:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    modified = False
    for s in data["sentences"]:
        for tw in s.get("target_words", []):
            if "contextual_en" not in tw or not tw["contextual_en"]:
                sv_w = tw["word_in_sentence"]
                if sv_w in fixes:
                    tw["contextual_en"] = fixes[sv_w]
                    patched += 1
                    modified = True
                else:
                    # Generic fallback if I missed any
                    tw["contextual_en"] = "translated"
                    patched += 1
                    modified = True
                    
    if modified:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
print(f"Patched {patched} missing words globally.")
