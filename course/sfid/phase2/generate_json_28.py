import json
import re

text = """För länge sedan hade jag en ganska dålig vana. Jag brukade städa mitt hem och diska mitt i natten. Jag var vaken varje natt. Det var ett helt obegripligt fenomen. "Hur ofta?" frågade en vän mig igår. Ofta, svarade jag. Jag ville ha ett tyst ljud i mitt hus. Men jag bestämde mig för att ändra på mitt liv och bygga upp en ny rutin. Jag ville vakna mycket bättre och ha mer energi. Numera sover jag bra på natten, och därmed mår jag toppen. 

Jag vaknar tidigt varje dag. Ibland tar min morgonrutin bara någon minut. Jag brukar genast ta en dusch. Att stå i en varm dusch är avkopplande. Sen tar jag på mig passande kläder, eller till och med badkläder om jag ska bada, och fixar mitt hår. "Jag har inte tid." brukade jag säga. Hela tiden kände jag mig stressad och valde att exkludera viktiga saker. Men jag vill aldrig gå igenom den perioden igen. Jag drack ibland sprit, vilket var dåligt. Nu vill jag istället koppla av på rätt sätt. Min gamla period är idag helt bortglömd.

På fritiden har jag börjat springa utomhus. Jag köpte nyligen en form av dyr löparsko. Trots en otroligt hög prisnivå var det ett bra alternativ på vår marknad. Jag springer inte varje gång jag är ledig, men minst en gång varje vecka. Egentligen har jag som mål att springa exakt en gång i månaden/veckan enligt mitt träningsschema. "Jag har ingen aning om…" sa jag till mig själv när jag började. Jag visste inte om jag kunde springa länge, men jag accepterar den tid det tar. Det får ta så lång tid det behöver. 

Så småningom vill jag springa närmare milen. Kanske om en månad kan jag klara fem kilometer, eller om ett halvår. Nästa år kanske jag klarar hela vägen. Jag hoppas kunna behålla denna fantastiska rutin alltid. På kvällskursen i svenska lär vi oss vilken tidspreposition man ska använda när man pratar om tid. Vi lär oss också att böja verb. När en vän brukar ringa på min dörr numera, har jag redan sprungit och är full av energi!"""

core_words = [
    "ibland", "hem", "städa", "hus", "löparsko", "Ofta", "Hur ofta?", "gång", 
    "en gång i månaden/veckan", "länge", "så lång tid", "den tid det tar", "minut", 
    "hela tiden", "alltid", "om en månad", "halvår", "nästa år", "liv", "aldrig", 
    "kläder", "hår", "tid", "natt", "på natten", "vakna", "dusch", "ta en dusch", 
    "tidspreposition", "vecka", "diska", "vana", "varje gång", "Jag har inte tid.", 
    "igår", "badkläder", "på fritiden", "dag"
]

glue_words = [
    "därmed", "prisnivå", "så småningom", "passande", "för länge sedan", 
    "alternativ", "närmare", "Jag har ingen aning om…", "sprit", "koppla", 
    "gå igenom", "form av", "behålla", "marknad", "ljud", "bortglömd", "ringa på", 
    "bygga upp", "fenomen", "mycket bättre", "böja", "exkludera"
]

target_mappings = [
    # Core
    ("ibland", "Ibland"),
    ("hem", "hem"),
    ("städa", "städa"),
    ("hus", "hus"),
    ("löparsko", "löparsko"),
    ("Ofta", "Ofta"),
    ("Hur ofta?", "Hur ofta?"),
    ("gång", "gång"),
    ("en gång i månaden/veckan", "en gång i månaden/veckan"),
    ("länge", "länge"),
    ("så lång tid", "så lång tid"),
    ("den tid det tar", "den tid det tar"),
    ("minut", "minut"),
    ("hela tiden", "Hela tiden"),
    ("alltid", "alltid"),
    ("om en månad", "om en månad"),
    ("halvår", "halvår"),
    ("nästa år", "Nästa år"),
    ("liv", "liv"),
    ("aldrig", "aldrig"),
    ("kläder", "kläder"),
    ("hår", "hår"),
    ("tid", "tid"),
    ("natt", "natt"),
    ("på natten", "på natten"),
    ("vakna", "vakna"),
    ("dusch", "dusch"),
    ("ta en dusch", "ta en dusch"),
    ("tidspreposition", "tidspreposition"),
    ("vecka", "vecka"),
    ("diska", "diska"),
    ("vana", "vana"),
    ("varje gång", "varje gång"),
    ("Jag har inte tid.", "Jag har inte tid."),
    ("igår", "igår"),
    ("badkläder", "badkläder"),
    ("på fritiden", "På fritiden"),
    ("dag", "dag"),

    # Glue
    ("därmed", "därmed"),
    ("prisnivå", "prisnivå"),
    ("så småningom", "Så småningom"),
    ("passande", "passande"),
    ("för länge sedan", "För länge sedan"),
    ("alternativ", "alternativ"),
    ("närmare", "närmare"),
    ("Jag har ingen aning om…", "Jag har ingen aning om…"),
    ("sprit", "sprit"),
    ("koppla", "koppla"),
    ("gå igenom", "gå igenom"),
    ("form av", "form av"),
    ("behålla", "behålla"),
    ("marknad", "marknad"),
    ("ljud", "ljud"),
    ("bortglömd", "bortglömd"),
    ("ringa på", "ringa på"),
    ("bygga upp", "bygga upp"),
    ("fenomen", "fenomen"),
    ("mycket bättre", "mycket bättre"),
    ("böja", "böja"),
    ("exkludera", "exkludera")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if base == "natt":
        start = text.find("varje natt") + 6
    elif base == "gång":
        start = text.find("minst en gång") + 9
    elif base == "tid":
        start = text.find("om tid.") + 3
    elif base == "dusch":
        start = text.find("varm dusch") + 5
    elif " " in word_in_sentence or "." in word_in_sentence or "?" in word_in_sentence or "!" in word_in_sentence or "…" in word_in_sentence or "”" in word_in_sentence or "-" in word_in_sentence or "–" in word_in_sentence or "/" in word_in_sentence or ")" in word_in_sentence or "," in word_in_sentence:
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
    "step_id": "vardagsliv",
    "step_title": "Vardagsliv",
    "article_id": "art_28",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('./course/sfid/phase2/article_28.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
