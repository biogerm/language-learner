import json
import re

text = """Jag har inte något emot att vara ute i naturen, särskilt när vi för en månad sedan besökte en ny miljöcertifierad park. Den ligger tusen meter över havet, med en underbar utsikt över en klar himmel. Vi bodde i en stor trädkoja byggd av rent trä. Stämningen var informell och man tar hållbarhet på allvar. "Detta verkar vara en fantastisk plats," sa jag. "Det tycker jag också." svarade min vän. Min vän är en känd idrottsstjärna som vill vara miljömedveten.

"Naturen här är en riktig berg -och dalbana," skrattade han, eftersom landskapet går mycket upp och ner. Vi hade en diskussion om miljö. Det finns en viktig skillnad mellan gammal och ny forkning om djurens beteende. Däremot är alla överens om att vår ursprungliga natur är bäst. Inom parken försöker man driva ett stort reningsverk på högvarv för att minska alla utsläpp som gör att vår flod kan bli förorenad. Sällan ser man en så ren vattenyta som här, och den kommer ofta på första plats i landet. Många vill vara en miljövänlig besökare, vilket är en klok åsikt. 

I somras kunde vi se skogen växa under en varm sommar. Nu, från kall gryning till mörk skymning, är själva skogen helt fantastisk. Där brukar man ha gott om vilda djur. Jag kan avslöja att vi såg en skadad höna som blev räddad. En vild kanin reste sig på sina bakben och bredvid den satt en liten mus och en råtta nära en sten. 

Man har valt att plantera in vissa djur för att rädda den lokala faunan. En lokal älgstam frodas och vi såg en stolt älgko. Dessutom fanns det en grävling, en liten vessla och till och med en flitig bäver. Man varnade oss för en giftig huggorm, men vi plockade ändå blåa bär medan ett surrande bi flög förbi. Min vän sa skämtsamt att han ville ta med sig en åsna nästa gång för att bära allt. Det var en fantastisk upplevelse. Ta reda på mer!"""

core_words = [
    "har inte något emot", "meter över havet", "berg -och dalbana", "trä", 
    "idrottsstjärna", "forkning", "beteende", "flod", "vattenyta", "ha gott om", 
    "utsläpp", "reningsverk", "miljömedveten", "miljövänlig", "trädkoja", 
    "hållbarhet", "miljöcertifierad", "kall", "växa", "sommar", "utsikt", "himmel", 
    "skymning", "gryning", "höna", "bär", "huggorm", "älgko", "vessla", "ursprunglig", 
    "åsna", "mus", "bi", "älgstam", "kanin", "giftig", "grävling", "bäver", "råtta", 
    "sten", "plantera in"
]

glue_words = [
    "månad", "däremot", "själva", "informell", "skillnad", "skadad", "på allvar", 
    "åsikt", "inom", "på första plats", "Det tycker jag också.", "sällan", 
    "som gör att", "verka vara", "avslöja", "bakben", "högvarv", "i somras", 
    "Ta reda på mer!"
]

target_mappings = [
    # Core
    ("har inte något emot", "har inte något emot"),
    ("meter över havet", "meter över havet"),
    ("berg -och dalbana", "berg -och dalbana"),
    ("trä", "trä"),
    ("idrottsstjärna", "idrottsstjärna"),
    ("forkning", "forkning"),
    ("beteende", "beteende"),
    ("flod", "flod"),
    ("vattenyta", "vattenyta"),
    ("ha gott om", "ha gott om"),
    ("utsläpp", "utsläpp"),
    ("reningsverk", "reningsverk"),
    ("miljömedveten", "miljömedveten"),
    ("miljövänlig", "miljövänlig"),
    ("trädkoja", "trädkoja"),
    ("hållbarhet", "hållbarhet"),
    ("miljöcertifierad", "miljöcertifierad"),
    ("kall", "kall"),
    ("växa", "växa"),
    ("sommar", "sommar"),
    ("utsikt", "utsikt"),
    ("himmel", "himmel"),
    ("skymning", "skymning"),
    ("gryning", "gryning"),
    ("höna", "höna"),
    ("bär", "bär"),
    ("huggorm", "huggorm"),
    ("älgko", "älgko"),
    ("vessla", "vessla"),
    ("ursprunglig", "ursprungliga"),
    ("åsna", "åsna"),
    ("mus", "mus"),
    ("bi", "bi"),
    ("älgstam", "älgstam"),
    ("kanin", "kanin"),
    ("giftig", "giftig"),
    ("grävling", "grävling"),
    ("bäver", "bäver"),
    ("råtta", "råtta"),
    ("sten", "sten"),
    ("plantera in", "plantera in"),

    # Glue
    ("månad", "månad"),
    ("däremot", "Däremot"),
    ("själva", "själva"),
    ("informell", "informell"),
    ("skillnad", "skillnad"),
    ("skadad", "skadad"),
    ("på allvar", "på allvar"),
    ("åsikt", "åsikt"),
    ("inom", "Inom"),
    ("på första plats", "på första plats"),
    ("Det tycker jag också.", "Det tycker jag också."),
    ("sällan", "Sällan"),
    ("som gör att", "som gör att"),
    ("verka vara", "verkar vara"),
    ("avslöja", "avslöja"),
    ("bakben", "bakben"),
    ("högvarv", "högvarv"),
    ("i somras", "I somras"),
    ("Ta reda på mer!", "Ta reda på mer!")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if base == "trä":
        start = text.find("rent trä") + 5
    elif base == "bär":
        start = text.find("blåa bär") + 5
    elif base == "bi":
        start = text.find("surrande bi") + 9
    elif base == "sten":
        start = text.find("en sten.") + 3
    elif " " in word_in_sentence or "." in word_in_sentence or "?" in word_in_sentence or "!" in word_in_sentence or "…" in word_in_sentence or "”" in word_in_sentence or "-" in word_in_sentence or "–" in word_in_sentence:
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
    "step_id": "natur_miljö",
    "step_title": "Natur & Miljö",
    "article_id": "art_20",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('./course/sfid/phase2/article_20.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
