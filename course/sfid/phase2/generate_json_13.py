import json
import re

text = """Jag är en riktig godisgris. För tio år sedan fick jag ofta höra av min lärare att jag hade ett sockerberoende. Då hade vi ofta dålig skolmat och det var alltid en brist på god mat och dryck. Därför var jag alltid jättehungrig och fikasugen när skoldagen var slut.

Idag bor jag långt ut på landet, där vårt lokala klimat är bra för odling av sockerbetor. Jag vet att bonden är stolt över sin sockerbeta. Ibland måste jag ta kontakt med bönderna. Min vän, som var en känd sockerbagare, sa att gamla traditioner måste leva vidare. Han brukade göra en massa fina saker, som en marsipantårta eller en liten pepparkaka full med söt karamell. Jag vet av andrahandsinformation att han en gång arbetade på en känd chokladfabrik. Det lät som ett underligt men fantastiskt ställe!

En dag kände jag att jag måste göra en paus i arbetet. Jag bestämde mig för att skaffa något gott till vår familjemiddag. Jag åkte till mitt smultronställe, en mysig godisbutik. Den såg annorlunda ut, nästan som en stor mataffär från en modern matvarukedja. "Du kan väl sätta dig en stund," sa ägaren. Det kändes bra. Jag gick omkring bland hyllorna medan jag tänkte på vad jag skulle välja. Jag ville ha något mer än bara frukt. 

Jag hittade en ny godissort, vilket var en liten geléfisk med härlig fruktsmak. Jag hittade också en fin pralin, en stor chokladkaka och en påse med polkagris. Dessutom köpte jag lördagsgodis, lite plockgodis och en rolig tablettask till barnen. Det fanns till och med en sötsak som en kokosboll och en god tårta. Allt detta var så långt från en texmexprodukt som man kan komma. 

Morgonen efter njöt jag av alltihop som en lyxig hotellfrukost. Säg vad ni vill, jag vet att det kanske får mig att inte se klok ut, men jag är så glad över mina godsaker. Man måste sortera vad som är viktigt i livet, annars blir det tråkigt. Ibland är det roligare att bara tugga på något gott."""

core_words = [
    "godisgris", "mat och dryck", "sockerberoende", "fikasugen", "familjemiddag", 
    "hotellfrukost", "plockgodis", "mataffär", "godissort", "matvarukedja", 
    "geléfisk", "fruktsmak", "texmexprodukt", "tårta", "pepparkaka", "sockerbeta", 
    "odling", "chokladfabrik", "godisbutik", "tablettask", "chokladkaka", "pralin", 
    "polkagris", "lördagsgodis", "karamell", "sötsak", "kokosboll", "marsipantårta", 
    "tugga", "söt", "frukt", "sockerbagare", "jättehungrig", "klimat", 
    "andrahandsinformation", "smultronställe", "lärare", "skolmat"
]

glue_words = [
    "göra en paus", "brist", "leva vidare", "riktig", "annars", "väl", "skaffa", 
    "annorlunda", "långt ut på landet", "sätta sig", "säg", "inte se klok ut", 
    "omkring", "full med", "en massa", "underlig", "ta kontakt med", "sortera", 
    "för…sedan", "så långt", "medan", "tänka på"
]

target_mappings = [
    # Core
    ("godisgris", "godisgris"),
    ("mat och dryck", "mat och dryck"),
    ("sockerberoende", "sockerberoende"),
    ("fikasugen", "fikasugen"),
    ("familjemiddag", "familjemiddag"),
    ("hotellfrukost", "hotellfrukost"),
    ("plockgodis", "plockgodis"),
    ("mataffär", "mataffär"),
    ("godissort", "godissort"),
    ("matvarukedja", "matvarukedja"),
    ("geléfisk", "geléfisk"),
    ("fruktsmak", "fruktsmak"),
    ("texmexprodukt", "texmexprodukt"),
    ("tårta", "tårta"),
    ("pepparkaka", "pepparkaka"),
    ("sockerbeta", "sockerbeta"),
    ("odling", "odling"),
    ("chokladfabrik", "chokladfabrik"),
    ("godisbutik", "godisbutik"),
    ("tablettask", "tablettask"),
    ("chokladkaka", "chokladkaka"),
    ("pralin", "pralin"),
    ("polkagris", "polkagris"),
    ("lördagsgodis", "lördagsgodis"),
    ("karamell", "karamell"),
    ("sötsak", "sötsak"),
    ("kokosboll", "kokosboll"),
    ("marsipantårta", "marsipantårta"),
    ("tugga", "tugga"),
    ("söt", "söt"),
    ("frukt", "frukt"),
    ("sockerbagare", "sockerbagare"),
    ("jättehungrig", "jättehungrig"),
    ("klimat", "klimat"),
    ("andrahandsinformation", "andrahandsinformation"),
    ("smultronställe", "smultronställe"),
    ("lärare", "lärare"),
    ("skolmat", "skolmat"),

    # Glue
    ("göra en paus", "göra en paus"),
    ("brist", "brist"),
    ("leva vidare", "leva vidare"),
    ("riktig", "riktig"),
    ("annars", "annars"),
    ("väl", "väl"),
    ("skaffa", "skaffa"),
    ("annorlunda", "annorlunda"),
    ("långt ut på landet", "långt ut på landet"),
    ("sätta sig", "sätta dig"),
    ("säg", "Säg"),
    ("inte se klok ut", "inte se klok ut"),
    ("omkring", "omkring"),
    ("full med", "full med"),
    ("en massa", "en massa"),
    ("underlig", "underligt"),
    ("ta kontakt med", "ta kontakt med"),
    ("sortera", "sortera"),
    ("för…sedan", "För tio år sedan"),
    ("så långt", "så långt"),
    ("medan", "medan"),
    ("tänka på", "tänkte på")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if base == "sockerbeta":
        start = text.find("sin sockerbeta") + 4
    elif base == "tårta":
        start = text.find("god tårta") + 4
    elif " " in word_in_sentence or "." in word_in_sentence or "?" in word_in_sentence or "!" in word_in_sentence or "…" in word_in_sentence:
        start = text.find(word_in_sentence)
    else:
        escaped = re.escape(word_in_sentence)
        match = re.search(r'\b' + escaped + r'\b', text)
        if match:
            start = match.start()
        else:
            start = text.find(word_in_sentence)
            
    if start == -1:
        print(f"ERROR: could not find '{word_in_sentence}' for base '{base}'")
        exit(1)
        
    end = start + len(word_in_sentence)
    words_json.append({
        "word_in_sentence": word_in_sentence,
        "base_form": base,
        "position_start": start,
        "position_end": end
    })

output = {
    "course_id": "sfid",
    "course_title": "SFI D",
    "step_id": "mat_matlagning",
    "step_title": "Mat & Matlagning",
    "article_id": "art_13",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('./course/sfid/phase2/article_13.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
