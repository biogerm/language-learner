import json
import re

text = """Ett nytt liv med en vän

I min tidiga barndom kände jag en snäll, gammal gumma. Hennes liv var mycket fascinerande. Hon brukade skriva ett långt inlägg i sin dagbok varje kväll om sina tankar. Hennes man brukade tyvärr ofta vara borta på resor, och det brukade ibland gå dåligt för honom i hans affärer. Han var ganska opålitlig och ofta olycklig över detta. 

För att inte vara ensam valde hon att köpa en hund. Det var en traditionell och lojal ras. Den nya hunden gav henne en oerhörd glädje, en riktig lyckokick i vardagen. Hunden var trofast, sällskaplig och otroligt hjälpsam hemma. Han var hur lugn som helst inomhus och var aldrig någonsin aggressiv.

Hon ville att allt i livet skulle vara så… som möjligt, nästan perfekt. Hunden hade en enorm betydelse för hennes gemenskap med andra människor. Hon brukade tjata på hunden att alltid vara lydig och ibland graciös, men hunden var istället ganska klumpig och mycket lekfull. Han var busig och stack ofta iväg, för att strax därefter snabbt följa efter henne hem igen. Han var nyfiken på allt nytt, men ibland framstod han som lite korkad.

Gummans alla vänner, och även hennes nära och kära, tyckte direkt att hunden var gullig. Han var självständig, men kunde också ibland skrämma grannarna när han plötsligt blev galen och sprang runt i cirklar. En gång hittade de en gammal, smutsig hundrakronorssedel som hunden glatt drog fram ur en buske med sin blöta näsa. De fick sedan var sin glass. 

Gumman var alltid generös och hon brukade regelbundet betala ut en del pengar till välgörenhet. Hon var kanske gammal men ändå väldigt påhittig. Ett riktigt spännande genombrott kom faktiskt när hon plötsligt blev en mycket framgångsrik lokal hundtränare. Hon kunde på så sätt fördubbla sina små inkomster, vilket skapade en fortsatt stabil och bra ekonomi för henne.

"Man behöver aldrig vara rädd för en trevlig hund," sa hon ofta. Hunden blev aldrig stressad eller desperat, och hon själv var aldrig rädd i hans trygga sällskap. 

"Ibland kan en vanlig dag kännas tråkig," sa hon ofta. "Men då måste man helt enkelt gilla läget och försöka se ljust på något trevligt som ändå händer. En bra hund är verkligen en sann vän. Allt kändes precis som förut när han var där." 

Ett fint minne jag har är hur hon brukade viska tyst till hunden och le stort mot honom. 
"Vi kommer alltid att längta efter dig när du reser bort," sa hon till mig, och jag kände absolut detsamma för henne. Hon var alltid väldigt förstående och enormt positiv. Hon avslutade alltid sina fina små brev till mig med orden puss puss."""

core_words = [
    "hjälpsam", "generös", "barndom", "galen", "traditionell", "desperat", 
    "viska", "le", "skrämma", "tråkig", "sällskaplig", "klumpig", "positiv", 
    "lyckokick", "trofast", "gilla läget", "lydig", "påhittig", "aggressiv", 
    "nära och kära", "längta efter", "lekfull", "nyfiken", "busig", "puss puss", 
    "tjata", "opålitlig", "korkad", "se ljust på något", "hur lugn som helst", 
    "graciös", "förstående", "gemenskap", "vara rädd", "gullig", "rädd", 
    "självständig", "olycklig"
]

glue_words = [
    "oerhörd", "välgörenhet", "betala ut", "så… som möjligt", "betydelse", 
    "var sin", "genombrott", "gå dåligt för", "fascinerande", "detsamma", 
    "vara borta", "minne", "näsa", "hundrakronorssedel", "sann", "förut", 
    "framgångsrik", "fortsatt", "fördubbla", "gumma", "inlägg", "följa efter"
]

target_mappings = [
    # Core
    ("hjälpsam", "hjälpsam"),
    ("generös", "generös"),
    ("barndom", "barndom"),
    ("galen", "galen"),
    ("traditionell", "traditionell"),
    ("desperat", "desperat"),
    ("viska", "viska"),
    ("le", "le"),
    ("skrämma", "skrämma"),
    ("tråkig", "tråkig"),
    ("sällskaplig", "sällskaplig"),
    ("klumpig", "klumpig"),
    ("positiv", "positiv"),
    ("lyckokick", "lyckokick"),
    ("trofast", "trofast"),
    ("gilla läget", "gilla läget"),
    ("lydig", "lydig"),
    ("påhittig", "påhittig"),
    ("aggressiv", "aggressiv"),
    ("nära och kära", "nära och kära"),
    ("längta efter", "längta efter"),
    ("lekfull", "lekfull"),
    ("nyfiken", "nyfiken"),
    ("busig", "busig"),
    ("puss puss", "puss puss"),
    ("tjata", "tjata"),
    ("opålitlig", "opålitlig"),
    ("korkad", "korkad"),
    ("se ljust på något", "se ljust på något"),
    ("hur lugn som helst", "hur lugn som helst"),
    ("graciös", "graciös"),
    ("förstående", "förstående"),
    ("gemenskap", "gemenskap"),
    ("vara rädd", "vara rädd"),
    ("gullig", "gullig"),
    ("rädd", "rädd"),
    ("självständig", "självständig"),
    ("olycklig", "olycklig"),

    # Glue
    ("oerhörd", "oerhörd"),
    ("välgörenhet", "välgörenhet"),
    ("betala ut", "betala ut"),
    ("så… som möjligt", "så… som möjligt"),
    ("betydelse", "betydelse"),
    ("var sin", "var sin"),
    ("genombrott", "genombrott"),
    ("gå dåligt för", "gå dåligt för"),
    ("fascinerande", "fascinerande"),
    ("detsamma", "detsamma"),
    ("vara borta", "vara borta"),
    ("minne", "minne"),
    ("näsa", "näsa"),
    ("hundrakronorssedel", "hundrakronorssedel"),
    ("sann", "sann"),
    ("förut", "förut"),
    ("framgångsrik", "framgångsrik"),
    ("fortsatt", "fortsatt"),
    ("fördubbla", "fördubbla"),
    ("gumma", "gumma"),
    ("inlägg", "inlägg"),
    ("följa efter", "följa efter")
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
    "step_id": "relationer_känslor",
    "step_title": "Relationer & Känslor",
    "article_id": "art_55",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('./course/sfid/phase2/article_55.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
