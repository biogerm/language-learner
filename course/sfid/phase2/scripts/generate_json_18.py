import json
import re

text = """"Hjälp mig!" ropade min vän när vi cyklade mountainbike. Banan var böjd och lite krånglig. "Nu förstår jag inte." fortsatte hon. Vi var i norr, i ett stort vildmarksområde. Min vän arbetar som pedagog och älskar vår underbara natur. Vi hade åkt hit för att uppleva allt från bergmansk dramatik till en stilla björkskog.

Jag ville rekonstruera en scen från filmen ”Det sjunde inseglet”. Min vän skrattade och tyckte att det var bättre att ta något att äta eller dricka. Det var en bra tidpunkt då en varm sol lyste. Vi satte oss vid en vacker blomma som också var vår lokala landskapsblomma. Hon började lära mig varje växtnamn och förklarade att man kan plantera dem för att få en naturlig och ekologisk utsmyckning runt sitt trähus.

"Visste du att två tredjedelar av Sveriges yta är skog?" frågade hon. Det brukade väcka intresse i varje klimatdebatt. I en stor älv, vår landets näst största, kunde man simma och fiska. Sveriges tredje största sjö är också populär.

Längs västra kusten är miljön mer klippig. Där brukar vi besöka det yttersta havsband och bygga ut små vindskydd. Det finns fina havsbad där barnen brukar fiska krabba och leta efter roliga skaldjur. En gång åkte vi på sälsafari och fick se en livs levande säl. Den var nästan lika stor som i naturlig storlek på museum. Vissa sälar kändes nästan lika orädda som en tam hund. 

Min väns bästa tips var att vandra i fjällen. Man går sakta över sten efter sten och plockar hjortron eller smultron. Man kan också stöta på ett vackert landskapsdjur. På kvällen kan märkliga saker inträffa. Innan solen går ner måste man slå läger. Det är vackert att se hur färgerna i luften sluta på rött. Men om man är längst upp i landet får man se en midnattsol och en klar stjärna. På grund av bristande kommunikation är området lugnt. Vissa bygger en utlramodern stuga, men det gamla vinner alltid."""

core_words = [
    "krånglig", "bergmansk", "”Det sjunde inseglet”", "smultron", "sol", "pedagog", 
    "växtnamn", "plantera", "rekonstruera", "landskapsblomma", "landskapsdjur", 
    "stjärna", "klippig", "skaldjur", "natur", "midnattsol", "säl", "vildmarksområde", 
    "kommunikation", "naturlig", "fiska krabba", "ta något att äta eller dricka", 
    "solen går ner", "näst störst", "älv", "hjortron", "fiska", "tam", 
    "vandra i fjällen", "mountainbike", "havsbad", "sten efter sten", "havsband", 
    "trähus", "klimatdebatt", "ekologisk", "björkskog", "naturlig storlek", 
    "utsmyckning", "blomma", "sälsafari"
]

glue_words = [
    "inträffa", "väcka intresse", "Nu förstår jag inte.", "böjd", "tredje största", 
    "sakta", "västra", "norr", "tips", "bygga ut", "Hjälp mig!", "slå", "sluta på", 
    "två tredjedelar", "utlramodern", "då", "simma", "stöta på", "underbar"
]

target_mappings = [
    # Core
    ("krånglig", "krånglig"),
    ("bergmansk", "bergmansk"),
    ("”Det sjunde inseglet”", "”Det sjunde inseglet”"),
    ("smultron", "smultron"),
    ("sol", "sol"),
    ("pedagog", "pedagog"),
    ("växtnamn", "växtnamn"),
    ("plantera", "plantera"),
    ("rekonstruera", "rekonstruera"),
    ("landskapsblomma", "landskapsblomma"),
    ("landskapsdjur", "landskapsdjur"),
    ("stjärna", "stjärna"),
    ("klippig", "klippig"),
    ("skaldjur", "skaldjur"),
    ("natur", "natur"),
    ("midnattsol", "midnattsol"),
    ("säl", "säl"),
    ("vildmarksområde", "vildmarksområde"),
    ("kommunikation", "kommunikation"),
    ("naturlig", "naturlig"),
    ("fiska krabba", "fiska krabba"),
    ("ta något att äta eller dricka", "ta något att äta eller dricka"),
    ("solen går ner", "solen går ner"),
    ("näst störst", "näst största"),
    ("älv", "älv"),
    ("hjortron", "hjortron"),
    ("fiska", "fiska"),
    ("tam", "tam"),
    ("vandra i fjällen", "vandra i fjällen"),
    ("mountainbike", "mountainbike"),
    ("havsbad", "havsbad"),
    ("sten efter sten", "sten efter sten"),
    ("havsband", "havsband"),
    ("trähus", "trähus"),
    ("klimatdebatt", "klimatdebatt"),
    ("ekologisk", "ekologisk"),
    ("björkskog", "björkskog"),
    ("naturlig storlek", "naturlig storlek"),
    ("utsmyckning", "utsmyckning"),
    ("blomma", "blomma"),
    ("sälsafari", "sälsafari"),

    # Glue
    ("inträffa", "inträffa"),
    ("väcka intresse", "väcka intresse"),
    ("Nu förstår jag inte.", "Nu förstår jag inte."),
    ("böjd", "böjd"),
    ("tredje största", "tredje största"),
    ("sakta", "sakta"),
    ("västra", "västra"),
    ("norr", "norr"),
    ("tips", "tips"),
    ("bygga ut", "bygga ut"),
    ("Hjälp mig!", "Hjälp mig!"),
    ("slå", "slå"),
    ("sluta på", "sluta på"),
    ("två tredjedelar", "två tredjedelar"),
    ("utlramodern", "utlramodern"),
    ("då", "då"),
    ("simma", "simma"),
    ("stöta på", "stöta på"),
    ("underbar", "underbara")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if base == "blomma":
        start = text.find("vacker blomma") + 7
    elif base == "naturlig":
        start = text.find("en naturlig och") + 3
    elif base == "fiska":
        start = text.find("och fiska.") + 4
    elif base == "då":
        start = text.find("tidpunkt då") + 9
    elif base == "säl":
        start = text.find("levande säl.") + 8
    elif " " in word_in_sentence or "." in word_in_sentence or "?" in word_in_sentence or "!" in word_in_sentence or "…" in word_in_sentence or "”" in word_in_sentence:
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
    "article_id": "art_18",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('./course/sfid/phase2/article_18.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
