import json
import re

text = """"–Hej! Det var länge sedan!" sa jag när jag mötte min gamla vän i skogen.
"Va?" sa hon. Sedan kände hon igen mig.
"Jag måste berätta en sak/en grej…" började hon. "Har du hört vad XX gjort?" frågade hon och log. 
"Nej, jag har ingen åsikt om kändisar," svarade jag bestämd. 
"Har du/ni hört att?" skämtade hon, "han ska ha planer på att abdikera från sitt jobb som personlig tränare!" Hennes berättelse kändes som en rolig abdikation från allvaret, men det var skönt att vara ute i naturen.

"Har du hört talas om …?" frågade hon och pekade på en gammal stenhäll. "Där finns en hällristning från ett tidigt århundrade. Det fanns en katolik som var känd för att ha rest hit dragen av sex hästar."

Hon hade en röd- och vitrandig jacka och en mintgrön mössa. Vi satte oss bland träden. "Det finns en missuppfattning om skogen. Vissa tror att djur kommer att anfalla, men de är ofta oskyldiga," sa hon. Vi köpte lite godis i lösvikt och lade en klick sylt på en bit bröd. Hon frågade om min vegan-korv gjord på havre. 
"Har du ätit det någon gång?" frågade jag. 
"Nej, det har jag aldrig gjort!" skrattade hon. Hon kunde inte låta bli att smaka. Smaken var jättestark och fick hennes ögon att svida.

Sedan pratade vi om vår natur. "På 70-talet under en högkonjunktur började den gröna vågen slå igenom. Folk ville ha ett naturligt kretslopp för allt från regn till avlopp," sa hon. Idag är en modern miljörörelse viktig i varje miljö- och klimatdebatt. Det engelska ordet climate syns i varje taggmoln online. 

Många unga vill engagera sig i miljön. Även min lilla guldfisk verkar vilja ha rent vatten! "Det är svårt att hinna med att bygga ett starkt skydd mot föroreningar, men vi måste motivera fler att acceptera fakta och inte överdriva rädslan," sa hon. Ibland känns det som om vi pratar på grönländska, ingen förstår varandra. Ett namn på problemet är okunskap. Det kändes bra att döpa problemen och förhoppningsvis få tillbaka hoppet. Innan vi gick kastade vi en snöboll mot ett litet apelsinträd i ett växthus. Vi riskerar att få problem om vi inte agerar, men vi kämpar på!"""

core_words = [
    "hällristning", "kretslopp", "taggmoln", "Har du ätit det någon gång?", 
    "Nej, det har jag aldrig gjort!", "korv", "havre", "mintgrön", "högkonjunktur", 
    "avlopp", "jättestark", "få problem", "miljörörelse", "gröna vågen", "slå igenom", 
    "miljö- och klimatdebatt", "climate", "hinna med", "skydd mot", "ute i naturen", 
    "dragen av sex hästar", "katolik", "abdikation", "apelsinträd", "abdikera", 
    "stenhäll", "känna igen", "ha planer", "grönländska", "personlig tränare", 
    "engagera sig i", "Har du hört vad XX gjort?", "Jag måste berätta en sak/en grej…", 
    "Har du hört talas om …?", "Har du/ni hört att?", "missuppfattning", "guldfisk", 
    "känd för att ha", "snöboll", "låta bli", "oskyldig"
]

glue_words = [
    "–Hej! Det var länge sedan!", "ingen åsikt", "bestämd", "anfalla", "vara", "bland", 
    "svida", "acceptera", "århundrade", "överdriva", "röd- och vitrandig", "Va?", "ung", 
    "namn", "få tillbaka", "döpa", "lösvikt", "klick", "motivera"
]

target_mappings = [
    # Core
    ("hällristning", "hällristning"),
    ("kretslopp", "kretslopp"),
    ("taggmoln", "taggmoln"),
    ("Har du ätit det någon gång?", "Har du ätit det någon gång?"),
    ("Nej, det har jag aldrig gjort!", "Nej, det har jag aldrig gjort!"),
    ("korv", "korv"),
    ("havre", "havre"),
    ("mintgrön", "mintgrön"),
    ("högkonjunktur", "högkonjunktur"),
    ("avlopp", "avlopp"),
    ("jättestark", "jättestark"),
    ("få problem", "få problem"),
    ("miljörörelse", "miljörörelse"),
    ("gröna vågen", "gröna vågen"),
    ("slå igenom", "slå igenom"),
    ("miljö- och klimatdebatt", "miljö- och klimatdebatt"),
    ("climate", "climate"),
    ("hinna med", "hinna med"),
    ("skydd mot", "skydd mot"),
    ("ute i naturen", "ute i naturen"),
    ("dragen av sex hästar", "dragen av sex hästar"),
    ("katolik", "katolik"),
    ("abdikation", "abdikation"),
    ("apelsinträd", "apelsinträd"),
    ("abdikera", "abdikera"),
    ("stenhäll", "stenhäll"),
    ("känna igen", "kände hon igen"),
    ("ha planer", "ha planer"),
    ("grönländska", "grönländska"),
    ("personlig tränare", "personlig tränare"),
    ("engagera sig i", "engagera sig i"),
    ("Har du hört vad XX gjort?", "Har du hört vad XX gjort?"),
    ("Jag måste berätta en sak/en grej…", "Jag måste berätta en sak/en grej…"),
    ("Har du hört talas om …?", "Har du hört talas om …?"),
    ("Har du/ni hört att?", "Har du/ni hört att?"),
    ("missuppfattning", "missuppfattning"),
    ("guldfisk", "guldfisk"),
    ("känd för att ha", "känd för att ha"),
    ("snöboll", "snöboll"),
    ("låta bli", "låta bli"),
    ("oskyldig", "oskyldiga"),

    # Glue
    ("–Hej! Det var länge sedan!", "–Hej! Det var länge sedan!"),
    ("ingen åsikt", "ingen åsikt"),
    ("bestämd", "bestämd"),
    ("anfalla", "anfalla"),
    ("vara", "vara"),
    ("bland", "bland"),
    ("svida", "svida"),
    ("acceptera", "acceptera"),
    ("århundrade", "århundrade"),
    ("överdriva", "överdriva"),
    ("röd- och vitrandig", "röd- och vitrandig"),
    ("Va?", "Va?"),
    ("ung", "unga"),
    ("namn", "namn"),
    ("få tillbaka", "få tillbaka"),
    ("döpa", "döpa"),
    ("lösvikt", "lösvikt"),
    ("klick", "klick"),
    ("motivera", "motivera")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if base == "korv":
        start = text.find("vegan-korv") + 6
    elif base == "vara":
        start = text.find("vara ute i naturen")
    elif " " in word_in_sentence or "." in word_in_sentence or "?" in word_in_sentence or "!" in word_in_sentence or "…" in word_in_sentence or "”" in word_in_sentence or "-" in word_in_sentence or "–" in word_in_sentence or "/" in word_in_sentence:
        start = text.find(word_in_sentence)
    else:
        escaped = re.escape(word_in_sentence)
        match = re.search(r'\b' + escaped + r'\b', text)
        if match:
            start = match.start()
        else:
            start = text.find(word_in_sentence)
            
    if start == -1:
        print(f"ERROR: could not find {word_in_sentence} for {base}")
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
    "step_id": "natur_miljö",
    "step_title": "Natur & Miljö",
    "article_id": "art_19",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('./course/sfid/phase2/article_19.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
