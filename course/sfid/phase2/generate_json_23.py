import json
import re

text = '''För två veckor sedan började jag jobba på en ny avdelning. Jag är en sjuksköterska och jag trivs mycket bra. Det är mitt tredje jobb i min 30-årsålder. Jag hjälper en läkare, även kallad doktor i vardagligt tal. Han har en stor vishet. Vi måste ta hand om patienter som är sjuka utan avbrott.

En patient, en gammal sjöman, hade allvarliga problem med hjärtat. Han var också psykiskt sjuk och hade ett svårt spelberoende samt ett gammalt narkotikaberoende. Han sa ofta att han var en tidigare narkoman. Det är tyvärr ett beroende som kan indirekt påverka hela kroppen negativt. Innan dess hade han också varit röksugen och brukade röka tre askar cigaretter om dagen. Hans tandhälsa var extremt dålig med mycket karies i varje tand. 

Man måste bestämma sig för att ändra på sitt liv. En stor hälsodebatt i samhället handlar om hur man ska/skall skydda människor från att komma för nära droger. Men oberoende av orsak, måste vi vara tålmodiga och sköta om alla lika väl. 

I ett annat rum låg en kvinna med en allvarlig virussjukdom och extremt hög kroppstemperatur. Det var kanske en fästingsjukdom eftersom hon hade haft bitande insekter på sig. Sådana insekter gillar vanligt djurblod, men också människans blod. En insekt hade bitit henne rakt i en blodåder, vilket gav henne en svår värk. Det kändes som om smärtan skulle explodera. Hennes sjukdom var fortfarande mystisk. 

Vissa dagar känner jag mig ointresserad, men oftast älskar jag mitt jobb på detta sjukhus. Även när det är mycket pratande med patienter så blir jag glad. Man kan ibland tröttna på systemet, som att sjuklön bara betalas ut om man drar ett streck på ett papper. Och vart åttonde år måste vi uppdatera licenser, vilket vi genast glömmer. Vi brukar sätta på en bra låt och applicera en skön hudkräm när passet är slut. 

När jag gick hem sa min chef: "Sköt om dig!" 
Jag log och svarade: "Hälsa …! ja, hälsa din familj från mig!"
Se hela ordlistan nedan.'''

core_words = [
    "psykiskt sjuk", "tröttna på", "sjuk", "problem med hjärtat", "doktor", 
    "läkare", "tålmodig", "sjuklön", "Sköt om dig!", "Hälsa …!", "oberoende av", 
    "sjuksköterska", "ta hand om", "sköta om", "bitande", "blod", "djurblod", 
    "sjukdom", "fästingsjukdom", "blodåder", "sjukhus", "värk", "virussjukdom", 
    "kroppstemperatur", "pratande", "hälsodebatt", "röka", "cigarett", "beroende", 
    "spelberoende", "narkotikaberoende", "hudkräm", "narkoman", "röksugen", 
    "karies", "tandhälsa", "tand"
]

glue_words = [
    "nedan", "utan avbrott", "vart åttonde år", "ändra på", "bestämma sig", 
    "ointresserad", "för två veckor sedan", "explodera", "tre", "innan dess", 
    "genast", "så", "sjöman", "trivas", "indirekt", "vishet", "streck", 
    "komma för nära", "även kallad", "tredje", "sätta på", "ska/skall", "30-årsålder"
]

target_mappings = [
    # Core
    ("psykiskt sjuk", "psykiskt sjuk"),
    ("tröttna på", "tröttna på"),
    ("sjuk", "sjuka"),
    ("problem med hjärtat", "problem med hjärtat"),
    ("doktor", "doktor"),
    ("läkare", "läkare"),
    ("tålmodig", "tålmodiga"),
    ("sjuklön", "sjuklön"),
    ("Sköt om dig!", "Sköt om dig!"),
    ("Hälsa …!", "Hälsa …!"),
    ("oberoende av", "oberoende av"),
    ("sjuksköterska", "sjuksköterska"),
    ("ta hand om", "ta hand om"),
    ("sköta om", "sköta om"),
    ("bitande", "bitande"),
    ("blod", "blod"),
    ("djurblod", "djurblod"),
    ("sjukdom", "sjukdom"),
    ("fästingsjukdom", "fästingsjukdom"),
    ("blodåder", "blodåder"),
    ("sjukhus", "sjukhus"),
    ("värk", "värk"),
    ("virussjukdom", "virussjukdom"),
    ("kroppstemperatur", "kroppstemperatur"),
    ("pratande", "pratande"),
    ("hälsodebatt", "hälsodebatt"),
    ("röka", "röka"),
    ("cigarett", "cigaretter"),
    ("beroende", "beroende"),
    ("spelberoende", "spelberoende"),
    ("narkotikaberoende", "narkotikaberoende"),
    ("hudkräm", "hudkräm"),
    ("narkoman", "narkoman"),
    ("röksugen", "röksugen"),
    ("karies", "karies"),
    ("tandhälsa", "tandhälsa"),
    ("tand", "tand"),

    # Glue
    ("nedan", "nedan"),
    ("utan avbrott", "utan avbrott"),
    ("vart åttonde år", "vart åttonde år"),
    ("ändra på", "ändra på"),
    ("bestämma sig", "bestämma sig"),
    ("ointresserad", "ointresserad"),
    ("för två veckor sedan", "För två veckor sedan"),
    ("explodera", "explodera"),
    ("tre", "tre"),
    ("innan dess", "Innan dess"),
    ("genast", "genast"),
    ("så", "så"),
    ("sjöman", "sjöman"),
    ("trivas", "trivs"),
    ("indirekt", "indirekt"),
    ("vishet", "vishet"),
    ("streck", "streck"),
    ("komma för nära", "komma för nära"),
    ("även kallad", "även kallad"),
    ("tredje", "tredje"),
    ("sätta på", "sätta på"),
    ("ska/skall", "ska/skall"),
    ("30-årsålder", "30-årsålder")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if base == "blod":
        start = text.find("människans blod") + 11
    elif base == "beroende":
        start = text.find("ett beroende som kan") + 4
    elif base == "sjukdom":
        start = text.find("Hennes sjukdom var") + 7
    elif base == "så":
        start = text.find("så blir jag")
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
    "step_id": "hälsa_medicin",
    "step_title": "Hälsa & Medicin",
    "article_id": "art_23",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('./course/sfid/phase2/article_23.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
