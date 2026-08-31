import json
import re

text = """När sommaren började närma sig, ville jag fira och festa varje helg. Efter många lata dagar var jag extremt partysugen och ville starta min semester på en stor musikfestival. Först var jag tvungen att boka boende i god tid. Jag hittade en plats bakom ett stort varuhus i närheten, och min plan var att ställa en vagn där ifall det skulle börja regna. 

"Gillar du festivaler?" frågade min vän, som var en känd finlandssvensk sångare och artist. 
"Jo, det är helt okej." sa jag och log stort. 
"På vilket sätt?" frågade han då. 
"Festivaler är en del av min identitet, och ungdomskultur är viktig för mig på många olika sätt", svarade jag.

Denna festival var som en mäktig konst- och industriutställning, och här fanns även spännande matkultur. Man kunde äta en stor festmåltid med lokalt kött och färskt bröd. Det kunde ofta tillkomma avgifter för maten, men det var guld värt ändå.

I slutet av kvällen skulle en känd musiker som hette Stry spela hög punkmusik. Hans röst var kristallklar och energin var enorm. 
"Det låter hemskt!" ropade min andra kompis med viss skepsis. Han gillade absolut inte hög musik. Istället för att lyssna, föredrog han att gå på en tyst biograf. 

Han gjorde en jättesnabb sökning på sin smart mobil, tittade på en digital karta och visade oss vägen. Vi hade rest genom stora delar av norra Sverige.
"Jag såg en fantastisk deckare nyligen. Det var min favoritfilm," sa han entusiastiskt. "Filmen utspelar sig i kallaste Norrland. Filmen handlar om… ett allvarligt brott. Filmen bygger på en bok av… en känd författare, på engelska kallad en book. Filmen bygger på en verklig händelse." 
"Spännande!" sa jag. "Själv gillar jag komedi och läskig skräckfilm." 
"Den var urkul," sa min vän. 

Dagen efter deltog vi i en traditionell bryggdans. All denna festlighet kunde fungera som en positiv förändring i våra liv. Vid kontakt med så mycket glädje kände jag att glädjen kunde ta fart på riktigt. Jag började till och med skriva om en gammal dikt, och tänkte på svensk grammatik och vad ett perfekt particip är. Om jag var ekonomiskt oberoende skulle jag leva så här för alltid."""

core_words = [
    "komedi", "deckare", "skräckfilm", "favoritfilm", "urkul", "bryggdans", 
    "en del av", "musikfestival", "lata dagar", "festa", "boka boende", 
    "fungera som", "stora delar av", "Norrland", "bröd", "partysugen", 
    "konst- och industriutställning", "stry", "fira", "karta", "matkultur", 
    "Filmen handlar om…", "Filmen utspelar sig i", "Filmen bygger på en bok av…", 
    "book", "Filmen bygger på en verklig händelse.", "skriva om", "biograf", 
    "festmåltid", "perfekt particip", "punkmusik", "ta fart", "smart mobil", 
    "varuhus", "artist", "festlighet", "vagn", "sångare", "ungdomskultur"
]

glue_words = [
    "starta", "absolut inte", "Det låter hemskt!", "förändring", 
    "på många olika sätt", "mäktig", "kristallklar", "istället för", 
    "jättesnabb", "i slutet av", "guld", "Jo, det är helt okej.", 
    "i närheten", "ifall", "närma sig", "finlandssvensk", 
    "ekonomiskt oberoende", "På vilket sätt?", "vid kontakt med", 
    "skepsis", "tillkomma"
]

target_mappings = [
    # Core
    ("komedi", "komedi"),
    ("deckare", "deckare"),
    ("skräckfilm", "skräckfilm"),
    ("favoritfilm", "favoritfilm"),
    ("urkul", "urkul"),
    ("bryggdans", "bryggdans"),
    ("en del av", "en del av"),
    ("musikfestival", "musikfestival"),
    ("lata dagar", "lata dagar"),
    ("festa", "festa"),
    ("boka boende", "boka boende"),
    ("fungera som", "fungera som"),
    ("stora delar av", "stora delar av"),
    ("Norrland", "Norrland"),
    ("bröd", "bröd"),
    ("partysugen", "partysugen"),
    ("konst- och industriutställning", "konst- och industriutställning"),
    ("stry", "Stry"),
    ("fira", "fira"),
    ("karta", "karta"),
    ("matkultur", "matkultur"),
    ("Filmen handlar om…", "Filmen handlar om…"),
    ("Filmen utspelar sig i", "Filmen utspelar sig i"),
    ("Filmen bygger på en bok av…", "Filmen bygger på en bok av…"),
    ("book", "book"),
    ("Filmen bygger på en verklig händelse.", "Filmen bygger på en verklig händelse."),
    ("skriva om", "skriva om"),
    ("biograf", "biograf"),
    ("festmåltid", "festmåltid"),
    ("perfekt particip", "perfekt particip"),
    ("punkmusik", "punkmusik"),
    ("ta fart", "ta fart"),
    ("smart mobil", "smart mobil"),
    ("varuhus", "varuhus"),
    ("artist", "artist"),
    ("festlighet", "festlighet"),
    ("vagn", "vagn"),
    ("sångare", "sångare"),
    ("ungdomskultur", "ungdomskultur"),

    # Glue
    ("starta", "starta"),
    ("absolut inte", "absolut inte"),
    ("Det låter hemskt!", "Det låter hemskt!"),
    ("förändring", "förändring"),
    ("på många olika sätt", "på många olika sätt"),
    ("mäktig", "mäktig"),
    ("kristallklar", "kristallklar"),
    ("istället för", "Istället för"),
    ("jättesnabb", "jättesnabb"),
    ("i slutet av", "I slutet av"),
    ("guld", "guld"),
    ("Jo, det är helt okej.", "Jo, det är helt okej."),
    ("i närheten", "i närheten"),
    ("ifall", "ifall"),
    ("närma sig", "närma sig"),
    ("finlandssvensk", "finlandssvensk"),
    ("ekonomiskt oberoende", "ekonomiskt oberoende"),
    ("På vilket sätt?", "På vilket sätt?"),
    ("vid kontakt med", "Vid kontakt med"),
    ("skepsis", "skepsis"),
    ("tillkomma", "tillkomma")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if base == "en del av":
        start = text.find("en del av")
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
    "article_id": "art_37",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('course/sfid/phase2/article_37.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
