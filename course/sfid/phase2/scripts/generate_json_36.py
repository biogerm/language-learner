import json
import re

text = """Jag älskar konst. Jag har alltid varit en person som vill utforska konsthistoria. Därför bestämde jag mig för att gå en konstutbildning. Till en början var det svårt att minnas varje bokstav i den teoretiska boken, men jag gillade att sitta i min ateljé och rita i min övningsbok. Jag försökte även göra en teckning och lite nakenmåleri. Varje besökare i mitt lilla galleri brukade ofta nämna hur mycket de älskade mitt vackra landskap. De kunde upptäcka spännande detaljer. "Visst låter det kul?" frågade jag min vän. "Det var väldigt kul att arbeta med det." Men för att tjäna pengar fick jag ibland erbjuda att dekorera hus med mina tavlor. 

Livet handlade inte bara om konst. Jag var också regissör. Jag försökte spela in en musikvideo med min bror. Han brukade ofta leka skådespelare och ville alltid spela död framför kameran. Vi skrev ett filmmanus som var en blandning av en mystisk myt, en actionfilm och en kärleksfilm. Den blev inspelad i svartvit färg, vilket var en konstig men snygg detalj. I ena scenen fick han trä upp pärlor på en hårig tråd. Troligtvis skulle filmen bli bra.

Senare skrev jag också en teaterpjäs. En känd skådespelerska, som för övrigt är singel, ville ha huvudrollen i min pjäs. Hon hade stor respekt för landets teatertradition, och hennes prestation skulle motsvara alla förväntningar. Men tyvärr blev hon sjuk. Hon fick ta antibiotika i flera veckor för att inte dö av infektionen. Hon var tvungen att gå ur projektet och vi fick byta namn på produktionen. Sådan är branschen. Det brukar vara så här ibland.

När jag inte jobbar älskar jag fredagsmys. Istället för att gå på bio gillar jag att spela ett parti schack. Jag har också skrivit en bra roman. En kollega frågade: "Vad tycker du om konstitutionell rätt, eller OS som hålls vart fjärde år?" Jag svarade: "Nja… Jag vill bara tänka på kultur. Kommer du förresten att komma ihåg vår roliga julfest ännu om tio år? Du då?" Jag log och tänkte att det var en härlig bit av mitt liv."""

core_words = [
    "galleri", "ateljé", "konstutbildning", "teckning", "konsthistoria", 
    "nakenmåleri", "roman", "singel", "skådespelare", "konstig", "leka", 
    "troligtvis", "antibiotika", "spela in", "spela död", "fredagsmys", 
    "Visst låter det kul?", "musikvideo", "gå på bio", "bokstav", 
    "konstitutionell", "övningsbok", "kul", "vart fjärde år", "teatertradition", 
    "regissör", "filmmanus", "teaterpjäs", "pjäs", "svartvit", "myt", 
    "ett parti schack", "skådespelerska", "trä upp", "gå ur", "julfest", 
    "konst", "actionfilm", "kärleksfilm"
]

glue_words = [
    "Nja…", "bit", "dekorera", "mystisk", "byta namn", "nämna", "så här", 
    "erbjuda", "landskap", "dö", "sådan", "upptäcka", "en", "komma ihåg", 
    "Du då?", "till en början", "ena", "ännu", "besökare", "hårig", "motsvara"
]

target_mappings = [
    # Core
    ("galleri", "galleri"),
    ("ateljé", "ateljé"),
    ("konstutbildning", "konstutbildning"),
    ("teckning", "teckning"),
    ("konsthistoria", "konsthistoria"),
    ("nakenmåleri", "nakenmåleri"),
    ("roman", "roman"),
    ("singel", "singel"),
    ("skådespelare", "skådespelare"),
    ("konstig", "konstig"),
    ("leka", "leka"),
    ("troligtvis", "Troligtvis"),
    ("antibiotika", "antibiotika"),
    ("spela in", "spela in"),
    ("spela död", "spela död"),
    ("fredagsmys", "fredagsmys"),
    ("Visst låter det kul?", "Visst låter det kul?"),
    ("musikvideo", "musikvideo"),
    ("gå på bio", "gå på bio"),
    ("bokstav", "bokstav"),
    ("konstitutionell", "konstitutionell"),
    ("övningsbok", "övningsbok"),
    ("kul", "kul"),
    ("vart fjärde år", "vart fjärde år"),
    ("teatertradition", "teatertradition"),
    ("regissör", "regissör"),
    ("filmmanus", "filmmanus"),
    ("teaterpjäs", "teaterpjäs"),
    ("pjäs", "pjäs"),
    ("svartvit", "svartvit"),
    ("myt", "myt"),
    ("ett parti schack", "ett parti schack"),
    ("skådespelerska", "skådespelerska"),
    ("trä upp", "trä upp"),
    ("gå ur", "gå ur"),
    ("julfest", "julfest"),
    ("konst", "konst"),
    ("actionfilm", "actionfilm"),
    ("kärleksfilm", "kärleksfilm"),

    # Glue
    ("Nja…", "Nja…"),
    ("bit", "bit"),
    ("dekorera", "dekorera"),
    ("mystisk", "mystisk"),
    ("byta namn", "byta namn"),
    ("nämna", "nämna"),
    ("så här", "så här"),
    ("erbjuda", "erbjuda"),
    ("landskap", "landskap"),
    ("dö", "dö"),
    ("sådan", "Sådan"),
    ("upptäcka", "upptäcka"),
    ("en", "en"),
    ("komma ihåg", "komma ihåg"),
    ("Du då?", "Du då?"),
    ("till en början", "Till en början"),
    ("ena", "ena"),
    ("ännu", "ännu"),
    ("besökare", "besökare"),
    ("hårig", "hårig"),
    ("motsvara", "motsvara")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if base == "en":
        start = text.find(" en ") + 1
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
    "article_id": "art_36",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('./course/sfid/phase2/article_36.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
