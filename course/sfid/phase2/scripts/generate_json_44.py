import json
import re

text = """Min svärdotter kom på besök i slutet på sommaren. Hon var politiskt aktiv i sitt hemland, en gammal bonderepublik, men hon ville flytta hit. Hon funderade på att emigrera för att få mer modern freedom och ett bättre liv. Hon ställde många frågor om hur det var att styra vårt land. 
"Sverige är indelat i många områden," började jag. "Varje kommun och landsting har ansvar för sin befolkning. De tar till exempel hand om lokal kollektivtrafik och all kommunal service. Om en vuxen invånare behöver hjälp, finns en effektiv socialtjänst som kan ge ett bra socialbidrag."

Hon hade en djup blick och började genast anteckna. "Vem bestämmer över riket?" frågade hon.
"Det finns en länsstyrelse regionalt, men i huvudstaden sitter vår stadsminister och bestämmer mycket. En viktig försvarsminister och en grön miljöminister arbetar på varsitt departement. Varje ministerpost är viktig. Folket får rösta i allmänna val, eftersom allmän rösträtt är en självklar rättighet. Vi skyddar medborgarna mot orättvis diskriminering genom våra grundlagar, som regeringsformen, tryckfrihetsförordningen och yttrandefrihetsgrundlagen."

Hon var tyst en stund, likt en tyst fånge inuti sin egen bubbla av tankar. 
"Det låter som ett ganska tryggt land. Det är möjligt." sa hon.
"Ja, och om en politiker bryter mot lagen kan folket sparka honom med omedelbar följd vid nästa val," sa jag och skrattade.

"Men är allt bara svår politik?" frågade hon. "Finns det någon rofylld och vilsam plats att besöka här i landet?"
"Självklart," sa jag. "Här långt ifrån all politik finns vacker natur. Man kan hitta lugn och ro i en varm och solig nationalpark. Kanske se en känd kunglighet eller en berömd världsartist på någon populär turistort. Staden Vimmerby är till exempel ett väldigt bra resmål där barnen kan träffa Pippi Långstrump. I landet finns till och med gamla statyer av en historisk nationalskald." 

"Låter skönt," sa hon. "Man skulle kunna…istället bara sitta och äta god husmanskost på en restaurang? Jag känner mig ganska rested nu efter resan."
"Absolut," sa jag och gav en liten varning. "Men kom ihåg att vi har haft högertrafik sedan 1967 när du kör bil hit."
Varje liten faktor spelar roll när man byter land, och vi hoppades verkligen att hon skulle återkomma någon gång. Hon ville nu först lugna ner sig med en god matbit och beställde sin favorit från caféet."""

core_words = [
    "försvarsminister", "miljöminister", "departement", "socialbidrag", 
    "länsstyrelse", "kollektivtrafik", "invånare", "kommunal", "socialtjänst", 
    "vilsam", "politiskt aktiv", "regeringsformen", "tryckfrihetsförordningen", 
    "freedom", "yttrandefrihetsgrundlagen", "rättighet", "landsting", 
    "ministerpost", "kommun", "befolkning", "rösta", "rösträtt", "svärdotter", 
    "nationalskald", "varm", "bonderepublik", "världsartist", "turistort", 
    "kunglighet", "fånge", "lugn och ro", "rofylld", "nationalpark", 
    "husmanskost", "högertrafik", "stadsminister", "Pippi Långstrump", 
    "varning", "resmål", "diskriminering"
]

glue_words = [
    "blick", "indelat", "sparka", "följd", "i slutet på", "återkomma", 
    "djup", "styra", "bubbla", "anteckna", "favorit", "lugna", "faktor", 
    "emigrera", "vuxen", "långt ifrån", "Det är möjligt.", "någon gång", 
    "rested", "Man skulle kunna…istället"
]

target_mappings = [
    # Core
    ("försvarsminister", "försvarsminister"),
    ("miljöminister", "miljöminister"),
    ("departement", "departement"),
    ("socialbidrag", "socialbidrag"),
    ("länsstyrelse", "länsstyrelse"),
    ("kollektivtrafik", "kollektivtrafik"),
    ("invånare", "invånare"),
    ("kommunal", "kommunal"),
    ("socialtjänst", "socialtjänst"),
    ("vilsam", "vilsam"),
    ("politiskt aktiv", "politiskt aktiv"),
    ("regeringsformen", "regeringsformen"),
    ("tryckfrihetsförordningen", "tryckfrihetsförordningen"),
    ("freedom", "freedom"),
    ("yttrandefrihetsgrundlagen", "yttrandefrihetsgrundlagen"),
    ("rättighet", "rättighet"),
    ("landsting", "landsting"),
    ("ministerpost", "ministerpost"),
    ("kommun", "kommun"),
    ("befolkning", "befolkning"),
    ("rösta", "rösta"),
    ("rösträtt", "rösträtt"),
    ("svärdotter", "svärdotter"),
    ("nationalskald", "nationalskald"),
    ("varm", "varm"),
    ("bonderepublik", "bonderepublik"),
    ("världsartist", "världsartist"),
    ("turistort", "turistort"),
    ("kunglighet", "kunglighet"),
    ("fånge", "fånge"),
    ("lugn och ro", "lugn och ro"),
    ("rofylld", "rofylld"),
    ("nationalpark", "nationalpark"),
    ("husmanskost", "husmanskost"),
    ("högertrafik", "högertrafik"),
    ("stadsminister", "stadsminister"),
    ("Pippi Långstrump", "Pippi Långstrump"),
    ("varning", "varning"),
    ("resmål", "resmål"),
    ("diskriminering", "diskriminering"),

    # Glue
    ("blick", "blick"),
    ("indelat", "indelat"),
    ("sparka", "sparka"),
    ("följd", "följd"),
    ("i slutet på", "i slutet på"),
    ("återkomma", "återkomma"),
    ("djup", "djup"),
    ("styra", "styra"),
    ("bubbla", "bubbla"),
    ("anteckna", "anteckna"),
    ("favorit", "favorit"),
    ("lugna", "lugna"),
    ("faktor", "faktor"),
    ("emigrera", "emigrera"),
    ("vuxen", "vuxen"),
    ("långt ifrån", "långt ifrån"),
    ("Det är möjligt.", "Det är möjligt."),
    ("någon gång", "någon gång"),
    ("rested", "rested"),
    ("Man skulle kunna…istället", "Man skulle kunna…istället")
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
    "article_id": "art_44",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('./course/sfid/phase2/article_44.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
