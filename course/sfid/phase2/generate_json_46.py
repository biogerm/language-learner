import json
import re

text = """"Vad sägs om att…? Vi kanske borde läsa en ny bok," föreslog jag för en svensk kompis. Han höll redan en tjock bok i handen.
"Vad handlar den om?" undrade han. 
"Det är en känd faktoid om makt och politik på tjugotalet och början av 1930-talet," förklarade jag.

Boken handlade om en oärlig finansman som nyligen var skild och valde att flytta hit från utlandet. Han ville introducera en helt ny typ av fond och en dyr aktie. Mannen var extremt fräck och använde sig av osjyst korruption. Han lyckades övertala flera förmögna investerare, till och med en italiensk greve och en rik norske företagare. Många av dessa var nära släkt med den tidens maktelit. "Hur mycket tjänar du?" frågade de ofta honom, och han lovade alltid att öka summan på deras bankkonto. De flesta av dem kunde bara se en framtida enorm rikedom. Finansmannen ville ur sin gamla fattigdom och valde tyvärr att stjäla från folket istället för att arbeta ärligt.

Snart uppstod en nationell ekonomisk kris. Det var svårt att veta vem som skulle tala för folket när staten ville höja varje litet pris. En vanlig arbetare hade nästan aldrig några besparingar, och få människor kunde ha råd att ens leva drägligt. Om man inte kunde uppge en stadig inkomst, kunde maten kosta mer än man någonsin hade tjänat. 

I varje land fanns det också en moralisk sanning som makthavarna blundade för. Det existerade ett hårt förtryck. Till exempel, under stora delar av 40-talet var homosexualitet fortfarande strängt förbjudet i Sverige. Att vara sig själv innebar att man skulle riskera att hamna i fängelse. Man kunde lätt gå vilse i lagboken och plötsligt vara skyldig till ett allvarligt brott. Det var verkligen en skamlig period i historien. En samtidig politiker försökte ge ett vettigt motargument i riksdagen, men det dröjde tyvärr innan folket fick riktig frihet. 

"Jag vet inte riktigt." sa min kompis tyst och började klappa sin trötta hund. "Det låter väldigt tungt. Men det är bra att staten slutade anmäla folk för kärlek. Idag kan man åtminstone leva öppet, vara stolt medlem i en vanlig idrottsförening eller donera en miljon till välgörenhet utan att det nödvändigtvis behöver synas i pressen." """

core_words = [
    "känd", "40-talet", "kosta", "1930-talet", "land", "svensk", "uppge", 
    "motargument", "nationell", "miljon", "oärlig", "kris", "frihet", 
    "Hur mycket tjänar du?", "höja", "aktie", "italiensk", "rikedom", 
    "idrottsförening", "skamlig", "fond", "anmäla", "fräck", "bankkonto", 
    "osjyst", "norske", "homosexualitet", "ha råd", "förbjudet", "pris", 
    "moralisk", "sanning", "tjugotalet", "riskera", "vara skyldig", 
    "hamna", "förtryck", "skild", "fängelse", "korruption"
]

glue_words = [
    "gå vilse", "samtidig", "Vad handlar den om?", "nästan aldrig", 
    "tala för", "ur", "stjäla", "leva", "bara", "rik", "nära släkt", 
    "övertala", "hit", "klappa", "öka", "introducera", "faktoid", 
    "synas", "Jag vet inte riktigt.", "Vad sägs om att…?"
]

target_mappings = [
    # Core
    ("känd", "känd"),
    ("40-talet", "40-talet"),
    ("kosta", "kosta"),
    ("1930-talet", "1930-talet"),
    ("land", "land"),
    ("svensk", "svensk"),
    ("uppge", "uppge"),
    ("motargument", "motargument"),
    ("nationell", "nationell"),
    ("miljon", "miljon"),
    ("oärlig", "oärlig"),
    ("kris", "kris"),
    ("frihet", "frihet"),
    ("Hur mycket tjänar du?", "Hur mycket tjänar du?"),
    ("höja", "höja"),
    ("aktie", "aktie"),
    ("italiensk", "italiensk"),
    ("rikedom", "rikedom"),
    ("idrottsförening", "idrottsförening"),
    ("skamlig", "skamlig"),
    ("fond", "fond"),
    ("anmäla", "anmäla"),
    ("fräck", "fräck"),
    ("bankkonto", "bankkonto"),
    ("osjyst", "osjyst"),
    ("norske", "norske"),
    ("homosexualitet", "homosexualitet"),
    ("ha råd", "ha råd"),
    ("förbjudet", "förbjudet"),
    ("pris", "pris"),
    ("moralisk", "moralisk"),
    ("sanning", "sanning"),
    ("tjugotalet", "tjugotalet"),
    ("riskera", "riskera"),
    ("vara skyldig", "vara skyldig"),
    ("hamna", "hamna"),
    ("förtryck", "förtryck"),
    ("skild", "skild"),
    ("fängelse", "fängelse"),
    ("korruption", "korruption"),

    # Glue
    ("gå vilse", "gå vilse"),
    ("samtidig", "samtidig"),
    ("Vad handlar den om?", "Vad handlar den om?"),
    ("nästan aldrig", "nästan aldrig"),
    ("tala för", "tala för"),
    ("ur", "ur"),
    ("stjäla", "stjäla"),
    ("leva", "leva"),
    ("bara", "bara"),
    ("rik", "rik"),
    ("nära släkt", "nära släkt"),
    ("övertala", "övertala"),
    ("hit", "hit"),
    ("klappa", "klappa"),
    ("öka", "öka"),
    ("introducera", "introducera"),
    ("faktoid", "faktoid"),
    ("synas", "synas"),
    ("Jag vet inte riktigt.", "Jag vet inte riktigt."),
    ("Vad sägs om att…?", "Vad sägs om att…?")
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
    "article_id": "art_46",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('./course/sfid/phase2/article_46.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
