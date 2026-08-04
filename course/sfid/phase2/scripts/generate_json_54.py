import json
import re

text = """Hejsan …
Kära … Anna,
Allt väl? Är allt bra med dig? 
Här är allting toppen/underbart/härligt på min nya semester.
Har du hört vad som har hänt? Det hände en så rolig sak … i lördags när jag skulle slå en signal till en gammal bekant. Vet du vem jag träffade? 
Jag mötte Peter! Vet du inte varför…? Han har ju flyttat tillbaka, fastän han trivdes bra utomlands. 

"Är det sant?" frågade jag honom. Han var snabb som en vessla på att hälsa på mig med en artig och trevlig bugning. Han sa att nuförtiden ser han väldigt trendig och äventyrlig ut. Det var en riktig ljuspunkt på dagen, en känsla av ren lycka att se honom. Jag kunde inte låta bli att fantisera om gamla tider, allt kändes som historia i koncentrat. 

Vi brukade alltid stötta varandra och han var en modig förebild för mig. Han ville utveckla sina idéer och var mycket lojal och extremt ärlig. 

"Tänker ni… flytta hit nu?" frågade jag. Han sa ja, men han hade en tendens att snabbt ångra sig. Man måste akta sig för att förlora sig själv helt och hållet i en stad. Han tyckte att staden blivit väldigt omodern och att han inte hittat lugnet någonstans, varken här eller ingen annanstans. 

"Man kan inte leva på andra," sa jag. "Du måste vara bussig och inte usel." 
"Nej, fy." sa han. "Jag skulle aldrig vara ofin. Det är icke en bra egenskap." Han var inte glad att behöva vara utan pengar.

Plötsligt kom en hysterisk kvinna fram och kastade en påse rakt i knät på honom! Hon bar en märklig, stickande parfym. 
"Lägg av!" skrek han. 

Han berättade att kvinnan trodde att han ville ha en affär med henne. Det är ibland svårt att lära känna människor ordentligt och man hinner inte känna någon väl innan det uppstår problem. 
"Hur länge?" frågade jag honom förvånat. 
"Ett bra tag," suckade han tyst. "Bry dig inte om … henne. Hon är en etablerad men helt hopplös person, ja, tänk dig/er att alltid behöva bråka." Jag kände mig tvungen att sjunka ner i min stol och fundera vidare. 

Jag hoppas att vi snart kan ses och njuta av en mysig fika. "Ha det så bra!" och "Du med /Du också." brukar vi ju skriva."""

core_words = [
    "slå en signal", "lycka", "ofin", "ljuspunkt", "Du med /Du också.", 
    "Kära …", "lojal", "stötta", "modig", "bekant", "hälsa", "Nej, fy.", 
    "hopplös", "äventyrlig", "Allt väl?", "fantisera", "förlora", 
    "helt och hållet", "känna någon väl", "Det hände en så rolig sak …", 
    "Här är allting toppen/underbart/härligt", "bussig", "lära känna", 
    "omodern", "ärlig", "usel", "Är allt bra med dig?", 
    "Har du hört vad som har hänt?", "ångra sig", "Hejsan …", 
    "Vet du vem jag träffade?", "förebild", "ha en affär", "akta sig", 
    "hysterisk", "Bry dig inte om …", "njuta av", "artig"
]

glue_words = [
    "tendens", "i knät", "ingen annanstans", "leva på andra", "nuförtiden", 
    "fastän", "trendig", "utveckla", "Hur länge?", "icke", "i koncentrat", 
    "stickande", "vara utan", "Vet du inte varför…?", "etablerad", 
    "snabb som en vessla", "Tänker ni…", "sjunka", "tänk dig/er", "vidare", 
    "Är det sant?", "Lägg av!"
]

target_mappings = [
    # Core
    ("slå en signal", "slå en signal"),
    ("lycka", "lycka"),
    ("ofin", "ofin"),
    ("ljuspunkt", "ljuspunkt"),
    ("Du med /Du också.", "Du med /Du också."),
    ("Kära …", "Kära …"),
    ("lojal", "lojal"),
    ("stötta", "stötta"),
    ("modig", "modig"),
    ("bekant", "bekant"),
    ("hälsa", "hälsa"),
    ("Nej, fy.", "Nej, fy."),
    ("hopplös", "hopplös"),
    ("äventyrlig", "äventyrlig"),
    ("Allt väl?", "Allt väl?"),
    ("fantisera", "fantisera"),
    ("förlora", "förlora"),
    ("helt och hållet", "helt och hållet"),
    ("känna någon väl", "känna någon väl"),
    ("Det hände en så rolig sak …", "Det hände en så rolig sak …"),
    ("Här är allting toppen/underbart/härligt", "Här är allting toppen/underbart/härligt"),
    ("bussig", "bussig"),
    ("lära känna", "lära känna"),
    ("omodern", "omodern"),
    ("ärlig", "ärlig"),
    ("usel", "usel"),
    ("Är allt bra med dig?", "Är allt bra med dig?"),
    ("Har du hört vad som har hänt?", "Har du hört vad som har hänt?"),
    ("ångra sig", "ångra sig"),
    ("Hejsan …", "Hejsan …"),
    ("Vet du vem jag träffade?", "Vet du vem jag träffade?"),
    ("förebild", "förebild"),
    ("ha en affär", "ha en affär"),
    ("akta sig", "akta sig"),
    ("hysterisk", "hysterisk"),
    ("Bry dig inte om …", "Bry dig inte om …"),
    ("njuta av", "njuta av"),
    ("artig", "artig"),

    # Glue
    ("tendens", "tendens"),
    ("i knät", "i knät"),
    ("ingen annanstans", "ingen annanstans"),
    ("leva på andra", "leva på andra"),
    ("nuförtiden", "nuförtiden"),
    ("fastän", "fastän"),
    ("trendig", "trendig"),
    ("utveckla", "utveckla"),
    ("Hur länge?", "Hur länge?"),
    ("icke", "icke"),
    ("i koncentrat", "i koncentrat"),
    ("stickande", "stickande"),
    ("vara utan", "vara utan"),
    ("Vet du inte varför…?", "Vet du inte varför…?"),
    ("etablerad", "etablerad"),
    ("snabb som en vessla", "snabb som en vessla"),
    ("Tänker ni…", "Tänker ni…"),
    ("sjunka", "sjunka"),
    ("tänk dig/er", "tänk dig/er"),
    ("vidare", "vidare"),
    ("Är det sant?", "Är det sant?"),
    ("Lägg av!", "Lägg av!")
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
    "article_id": "art_54",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('./course/sfid/phase2/article_54.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
