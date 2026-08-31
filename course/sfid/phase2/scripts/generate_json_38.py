import json
import re

text = """"Vet du vad jag har läst?" frågade jag min vän i vår telefon. "Det var en spännande tidningsartikel om en skröna som brukar sprida sig på internet vartannat år. Det är en rolig vandringshistoria om en svensk charterresenär som ringde till ett utrikesdepartement bara för skojs skull. Han sa att han var nära släkt med kungen."
"Det var underhållande, men vad hände sedan?" undrade hon.
"Jo, det var egentligen bara ett roligt skämt, typ ett stort aprilskämt", sa jag för att dra ut på historien.

Sedan frågade jag henne om hon ville följa med till en stor nöjespark i staden för att se en ny attraktion. 
"Jag kan tyvärr inte idag." svarade hon snabbt.
"Vad ville hon ha?" tänkte jag tyst för mig själv. "Hur klarar du dig?" frågade jag istället. "Vad gör du hela dagarna?"

Hon förklarade att hon inte gillade att bara ligga och lata sig. Istället ville hon idrotta och ha en aktiv fritidsvana. Hon hade en förvånansvärd stor samling av träningsutrustning. Hennes absolut bästa fritidsaktivitet var utförsåkning under en kall vinter. Varje timme på berget var viktig. Ibland kunde hon ta fram en gammal pjäxa och en stav från garaget och drömma om backen. "Det känns som en helt omöjlig uppgift att leva utan snön", sa hon. Inuti henne fanns det också väldigt mycket fantasi.

"Men när snön saknas, så gillar du väl en annan sport där man kan vinna en stor tävling? Kanske ridning eller snabb hästpolo? Eller spela innebandy med kompisar?" 
"Ja, dessutom älskar jag skridskoåkning. Jag sätter på mig min skridsko och åker på isen", svarade hon. "Men jag gillar inte all motorsport. Jag skulle aldrig köra en sportbil snabbt eller vara en av de så kallade tysta golfspelare som går runt."

Det fanns en tydlig åsikt i hennes val. Det verkade som att hennes passioner skulle höra hemma på ett aktivt läger. Lång transport till ett sådant läger var ibland svårt, särskilt när kläderna var täckta av jordig mark. Inte förrän hon kom hem kände hon sig trött. Hon sade ett gammalt citat om hälsa. 
"Men vill du inte gå på teater då och då?" frågade jag henne. 
"Kanske", sa hon med ett skratt, "men jag tycker faktiskt man borde avskaffa allt stillasittande i världen!"
"""

core_words = [
    "charterresenär", "utrikesdepartement", "idrotta", "golfspelare", 
    "motorsport", "Vet du vad jag har läst?", "skröna", "sprida", 
    "tidningsartikel", "vandringshistoria", "underhållande", "vartannat år", 
    "för skojs skull", "förvånansvärd", "sportbil", "saknas", "nöjespark", 
    "skämt", "aprilskämt", "transport", "stav", "tävling", "pjäxa", "samling", 
    "citat", "läger", "attraktion", "fritidsvana", "fantasi", "utförsåkning", 
    "hästpolo", "fritidsaktivitet", "gå på teater", "vinna", "ridning", 
    "skridsko", "innebandy", "sport", "skridskoåkning"
]

glue_words = [
    "dra", "telefon", "avskaffa", "vinter", "vad", "inuti", 
    "ligga och lata sig", "omöjlig", "timme", "jordig", "släkt med", 
    "ta fram", "Jag kan tyvärr inte idag.", "tydlig", "så kallade", 
    "höra hemma", "förrän", "Hur klarar du dig?", "dessutom", "då och då", 
    "Vad ville hon ha?"
]

target_mappings = [
    # Core
    ("charterresenär", "charterresenär"),
    ("utrikesdepartement", "utrikesdepartement"),
    ("idrotta", "idrotta"),
    ("golfspelare", "golfspelare"),
    ("motorsport", "motorsport"),
    ("Vet du vad jag har läst?", "Vet du vad jag har läst?"),
    ("skröna", "skröna"),
    ("sprida", "sprida"),
    ("tidningsartikel", "tidningsartikel"),
    ("vandringshistoria", "vandringshistoria"),
    ("underhållande", "underhållande"),
    ("vartannat år", "vartannat år"),
    ("för skojs skull", "för skojs skull"),
    ("förvånansvärd", "förvånansvärd"),
    ("sportbil", "sportbil"),
    ("saknas", "saknas"),
    ("nöjespark", "nöjespark"),
    ("skämt", "skämt"),
    ("aprilskämt", "aprilskämt"),
    ("transport", "transport"),
    ("stav", "stav"),
    ("tävling", "tävling"),
    ("pjäxa", "pjäxa"),
    ("samling", "samling"),
    ("citat", "citat"),
    ("läger", "läger"),
    ("attraktion", "attraktion"),
    ("fritidsvana", "fritidsvana"),
    ("fantasi", "fantasi"),
    ("utförsåkning", "utförsåkning"),
    ("hästpolo", "hästpolo"),
    ("fritidsaktivitet", "fritidsaktivitet"),
    ("gå på teater", "gå på teater"),
    ("vinna", "vinna"),
    ("ridning", "ridning"),
    ("skridsko", "skridsko"),
    ("innebandy", "innebandy"),
    ("sport", "sport"),
    ("skridskoåkning", "skridskoåkning"),

    # Glue
    ("dra", "dra"),
    ("telefon", "telefon"),
    ("avskaffa", "avskaffa"),
    ("vinter", "vinter"),
    ("vad", "vad"),
    ("inuti", "Inuti"),
    ("ligga och lata sig", "ligga och lata sig"),
    ("omöjlig", "omöjlig"),
    ("timme", "timme"),
    ("jordig", "jordig"),
    ("släkt med", "släkt med"),
    ("ta fram", "ta fram"),
    ("Jag kan tyvärr inte idag.", "Jag kan tyvärr inte idag."),
    ("tydlig", "tydlig"),
    ("så kallade", "så kallade"),
    ("höra hemma", "höra hemma"),
    ("förrän", "förrän"),
    ("Hur klarar du dig?", "Hur klarar du dig?"),
    ("dessutom", "dessutom"),
    ("då och då", "då och då"),
    ("Vad ville hon ha?", "Vad ville hon ha?")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if base == "vad":
        start = text.find("vad hände sedan")
    elif base == "sport":
        start = text.find(" annan sport ") + 7
    elif base == "skämt":
        start = text.find(" skämt,") + 1
    elif base == "skridsko":
        start = text.find("min skridsko ") + 4
    elif " " in word_in_sentence or "." in word_in_sentence or "?" in word_in_sentence or "!" in word_in_sentence or "…" in word_in_sentence or "”" in word_in_sentence or "-" in word_in_sentence or "–" in word_in_sentence or "/" in word_in_sentence or ")" in word_in_sentence or "," in word_in_sentence or "=" in word_in_sentence:
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
    "step_id": "kultur_nöje",
    "step_title": "Kultur & Nöje",
    "article_id": "art_38",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('course/sfid/phase2/article_38.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
