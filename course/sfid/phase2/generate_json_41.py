import json
import re

text = """En vanlig lördagskväll satt vi och tittade på en spännande teveserie och började fundera över livet. Jag var klädd i en svart basker, precis som en klassisk målare, men den var tyvärr för liten. 
"Vad tänker du göra när…?" frågade min kompis plötsligt, utan att avsluta meningen. Han var en duktig dektektiv, fast han också gillade att blogga om arkitektur och gammalt hantverk.
"Jag vet inte. Jag skulle vilja veta hur… man bygger en gigantisk minnesbyggnad," sa jag ärligt.

Vi var mycket intresserade av kultur, så vi bestämde oss för att passera en känd sevärdhet i staden, ett vackert slott. Där fanns en staty av massivt brons, en fantastisk bronsstaty. Plötsligt såg vi en gammal skvallertidning på marken. 
"Vad har hänt?" sa han och plockade upp den för att hitta ledtrådar. Tidningen hade en handling som verkade handla om en gammal folksaga om ett läskigt odjur. 
"Kanske kan ett riktigt odjur hoppa upp ur vattnet!" sa han.
"Överdriv!" skrek jag. "Du är alltid så sträng och intensiv." 

Senare hörde vi musik från en scen. Det var en känd popgrupp som skulle spela fiol, och det såg ut som en färgstark cirkus. På marken låg en lös kanonkula. "Vi måste se till att gömma den. Den kan orsaka skada," sa jag, men min vän ville bara låta den vara. 

Han ville istället ta med mig till ett stort diskotek där en discokula snurrade. Vi dansade jättemycket, men jag valde att stå över en Tangokurs som hölls där. Efteråt kände vi för ett äventyr och valde att ta ett dopp i sjön. Då började jag inse att det var mycket roligare än tråkig skidåkning eller snabbt rally. Vi pratade om den gamla filmen ”Fanny och Alexander”, en dokumentär vi sett hälften av, och om sjuttiotalets idéer kring fri sex. Allt detta inspirerade mig till att skriva en vacker dikt följande morgon, där min kompis var en sann hjälte."""

core_words = [
    "ta ett dopp", "odjur", "Tangokurs", "skidåkning", "discokula", "dikt", 
    "målare", "scen", "teveserie", "basker", "”Fanny och Alexander”", 
    "äventyr", "dokumentär", "handling", "spela", "sevärdhet", "skvallertidning", 
    "bronsstaty", "folksaga", "popgrupp", "slott", "brons", "dektektiv", 
    "cirkus", "diskotek", "fiol", "hjälte", "hantverk", "minnesbyggnad", 
    "fri sex", "rally", "arkitektur", "kanonkula", "blogga"
]

glue_words = [
    "handla om", "låta", "lördagskväll", "passera", "hitta", "ta med", 
    "Vad har hänt?", "för liten", "hälften av", "intresserade av", 
    "stå över", "inse", "gigantisk", "hoppa upp ur", "lös", "orsaka", 
    "överdriv!", "jättemycket", "Jag skulle vilja veta hur…", "fundera", 
    "följande", "se till att", "gömma", "Vad tänker du göra när…?", 
    "sträng", "intensiv"
]

target_mappings = [
    # Core
    ("ta ett dopp", "ta ett dopp"),
    ("odjur", "odjur"),
    ("Tangokurs", "Tangokurs"),
    ("skidåkning", "skidåkning"),
    ("discokula", "discokula"),
    ("dikt", "dikt"),
    ("målare", "målare"),
    ("scen", "scen"),
    ("teveserie", "teveserie"),
    ("basker", "basker"),
    ("”Fanny och Alexander”", "”Fanny och Alexander”"),
    ("äventyr", "äventyr"),
    ("dokumentär", "dokumentär"),
    ("handling", "handling"),
    ("spela", "spela"),
    ("sevärdhet", "sevärdhet"),
    ("skvallertidning", "skvallertidning"),
    ("bronsstaty", "bronsstaty"),
    ("folksaga", "folksaga"),
    ("popgrupp", "popgrupp"),
    ("slott", "slott"),
    ("brons", "brons"),
    ("dektektiv", "dektektiv"),
    ("cirkus", "cirkus"),
    ("diskotek", "diskotek"),
    ("fiol", "fiol"),
    ("hjälte", "hjälte"),
    ("hantverk", "hantverk"),
    ("minnesbyggnad", "minnesbyggnad"),
    ("fri sex", "fri sex"),
    ("rally", "rally"),
    ("arkitektur", "arkitektur"),
    ("kanonkula", "kanonkula"),
    ("blogga", "blogga"),

    # Glue
    ("handla om", "handla om"),
    ("låta", "låta"),
    ("lördagskväll", "lördagskväll"),
    ("passera", "passera"),
    ("hitta", "hitta"),
    ("ta med", "ta med"),
    ("Vad har hänt?", "Vad har hänt?"),
    ("för liten", "för liten"),
    ("hälften av", "hälften av"),
    ("intresserade av", "intresserade av"),
    ("stå över", "stå över"),
    ("inse", "inse"),
    ("gigantisk", "gigantisk"),
    ("hoppa upp ur", "hoppa upp ur"),
    ("lös", "lös"),
    ("orsaka", "orsaka"),
    ("överdriv!", "Överdriv!"),
    ("jättemycket", "jättemycket"),
    ("Jag skulle vilja veta hur…", "Jag skulle vilja veta hur…"),
    ("fundera", "fundera"),
    ("följande", "följande"),
    ("se till att", "se till att"),
    ("gömma", "gömma"),
    ("Vad tänker du göra när…?", "Vad tänker du göra när…?"),
    ("sträng", "sträng"),
    ("intensiv", "intensiv")
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
    "step_id": "kultur_nöje",
    "step_title": "Kultur & Nöje",
    "article_id": "art_41",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('./course/sfid/phase2/article_41.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
