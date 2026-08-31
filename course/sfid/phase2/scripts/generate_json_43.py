import json
import re

text = """Ett land kan ha olika statsskick. Vissa länder är en republik med en president och ibland en premiärminister, medan andra har en kung och en kronprins som måste tillhöra en stor kungafamilj. Tyvärr finns det också länder där en maktgalen diktator lyckas ta kontrollen genom en brutal statskupp. Då tvingas ofta en interimsregering att avgå, och politiska ledare kan till och med bli skjutna på öppen gata. I en demokrati måste man däremot bli vald av folket för att få sitta vid makten. 

Ett demokratiskt land styrs ofta av ett parlament. En parlamentsledamot representerar ett politiskt parti, och varje röst från en allmän folkomröstning räknas. Vissa väljare gillar ett stort, traditionellt parti, men andra väljer att placera sin röst på ett litet enfrågeparti. Vad har de för löften? Jo, i sitt valmanifest kan en partiledare lova jättemycket, till exempel förändringar om energi som kärnkraft eller om offentlig ekonomi. 

Vår kända regering består av många ministrar. Där finns en finansminister, en utrikesminister, en utbildningsminister, en kulturminister och andra viktiga statsråd. Deras uppgift är att hålla ordning och samarbeta med varje statlig myndighet. 

För sextio år sedan var samhället mycket mer ojämlikt, ett typiskt klassamhälle. Men sedan utvecklades en berömd välfärdststat. En välkänd socialdemokratisk rörelse ville bygga en bättre välfärd för varje medborgare i landet. Alla som hade barn fick barnbidrag, och de äldre fick en tilläggspension plus andra olika bidrag. Även om vi har ett relativt högt skattetryck i Sverige idag, så ger den typen av system en stor grundläggande trygghet. 

Politiken måste ständigt utvecklas i samband med tiden. Det är viktigt att stödja en samkönad familj, värna om miljön vid vår vackra kust, o.s.v. Jag brukar ofta associera politik med ansvar, eftersom politiska beslut lätt kan sluta väldigt illa om de är oförberedda. Man ska inte bara stå bredbent och göra en grandios entré som om man vore kung för en dag. Förresten, visste du att en republikansk rörelse ofta kan ha rötterna i gamla historiska traditioner?"""

core_words = [
    "republik", "premiärminister", "diktator", "parlament", 
    "parlamentsledamot", "parti", "regering", "kung", "kung för en dag", 
    "finansminister", "kungafamilj", "statsskick", "bli vald", "kronprins", 
    "valmanifest", "enfrågeparti", "republikansk", "partiledare", "röst", 
    "socialdemokratisk", "klassamhälle", "medborgare", "välfärd", 
    "välfärdststat", "barnbidrag", "tilläggspension", "bidrag", 
    "skattetryck", "ekonomi", "offentlig", "kärnkraft", "statskupp", 
    "sitta vid makten", "interimsregering", "på öppen gata", "myndighet", 
    "statsråd", "utrikesminister", "utbildningsminister", "kulturminister"
]

glue_words = [
    "bredbent", "o.s.v.", "den typen av", "sextio", "Vad", "samband", 
    "samkönad", "associera", "ordning", "lyckas", "tillhöra", "kust", 
    "sluta", "allmän", "entré", "ha rötterna i", "välkänd", "placera", 
    "berömd", "förresten"
]

target_mappings = [
    # Core
    ("republik", "republik"),
    ("premiärminister", "premiärminister"),
    ("diktator", "diktator"),
    ("parlament", "parlament"),
    ("parlamentsledamot", "parlamentsledamot"),
    ("parti", "parti"),
    ("regering", "regering"),
    ("kung", "kung"),
    ("kung för en dag", "kung för en dag"),
    ("finansminister", "finansminister"),
    ("kungafamilj", "kungafamilj"),
    ("statsskick", "statsskick"),
    ("bli vald", "bli vald"),
    ("kronprins", "kronprins"),
    ("valmanifest", "valmanifest"),
    ("enfrågeparti", "enfrågeparti"),
    ("republikansk", "republikansk"),
    ("partiledare", "partiledare"),
    ("röst", "röst"),
    ("socialdemokratisk", "socialdemokratisk"),
    ("klassamhälle", "klassamhälle"),
    ("medborgare", "medborgare"),
    ("välfärd", "välfärd"),
    ("välfärdststat", "välfärdststat"),
    ("barnbidrag", "barnbidrag"),
    ("tilläggspension", "tilläggspension"),
    ("bidrag", "bidrag"),
    ("skattetryck", "skattetryck"),
    ("ekonomi", "ekonomi"),
    ("offentlig", "offentlig"),
    ("kärnkraft", "kärnkraft"),
    ("statskupp", "statskupp"),
    ("sitta vid makten", "sitta vid makten"),
    ("interimsregering", "interimsregering"),
    ("på öppen gata", "på öppen gata"),
    ("myndighet", "myndighet"),
    ("statsråd", "statsråd"),
    ("utrikesminister", "utrikesminister"),
    ("utbildningsminister", "utbildningsminister"),
    ("kulturminister", "kulturminister"),

    # Glue
    ("bredbent", "bredbent"),
    ("o.s.v.", "o.s.v."),
    ("den typen av", "den typen av"),
    ("sextio", "sextio"),
    ("Vad", "Vad"),
    ("samband", "samband"),
    ("samkönad", "samkönad"),
    ("associera", "associera"),
    ("ordning", "ordning"),
    ("lyckas", "lyckas"),
    ("tillhöra", "tillhöra"),
    ("kust", "kust"),
    ("sluta", "sluta"),
    ("allmän", "allmän"),
    ("entré", "entré"),
    ("ha rötterna i", "ha rötterna i"),
    ("välkänd", "välkänd"),
    ("placera", "placera"),
    ("berömd", "berömd"),
    ("förresten", "Förresten")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if " " in word_in_sentence or "." in word_in_sentence or "?" in word_in_sentence or "!" in word_in_sentence or "…" in word_in_sentence or "”" in word_in_sentence or "-" in word_in_sentence or "–" in word_in_sentence or "/" in word_in_sentence or ")" in word_in_sentence or "," in word_in_sentence or "=" in word_in_sentence:
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
    "step_id": "samhälle_politik",
    "step_title": "Samhälle & Politik",
    "article_id": "art_43",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('course/sfid/phase2/article_43.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
