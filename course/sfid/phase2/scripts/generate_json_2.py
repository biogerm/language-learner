import json
import re

text = """Min kompis Anna är biliotekarie och gillar normalt sett att läsa böcker i fred. Men förra veckan bestämde hon sig för att åka iväg på en lång resa utomlands under sin ledighet. "Det är dags att åka på en riktig semester", sa hon glatt till mig.

Hon hade en mycket tung packning eftersom hon planerade att vandra i bergen. Innan hon skulle gå iväg till stationen, packade hon noggrant ner en karta och en kompass i sin väska. "Priserna har gått upp." tänkte hon, så hon valde ett billigt vandrarhem i en liten stad istället för ett dyrt lyxhotell. Hon hade också tänkt ta tåget, eftersom det är ett bra sätt att se en lång järnvägslinje. Men tyvärr var tåget inställt, så hon var tvungen att ta bussen. En snäll busschaufför hjälpte henne med väskan när hon klev på sin buss.

Snart var hon framme. När man är på väg till en ny plats är allting mycket spännande. Hon bestämde sig snabbt för att gå ner till en solig strand för att vila. På så sätt kunde hon njuta av den friska naturen. Sedan ville hon åka till en storstad för att gå på museum och se historiska utställningar.

Efter fyra dagar i naturen kände hon sig helt klar. "Jag måste veta vad som finns i stan," tänkte hon och hyrde ett praktiskt rum i centrum. Hennes nya rum var faktiskt inte mindre än det första. På morgonen gick hon ner på stan för att besöka en känd marknad. Hon var så glad att hon ville springa nerför hela gatan. Hon valde sedan att gå ut med sin kamera på en lång gata. Där såg hon någon rida på en häst förbi en stor bil. Det var en perfekt upplevelse, och hon började äntligen förstå hur roligt det verkligen är att resa. Hon försökte spara alla minnen.

Senare samma vecka skickade hon ett meddelande: "Du borde komma och hälsa på mig." Så jag bestämde mig för att åka och hälsa på henne på ett kort besök. "Ta samma väg som du kom." sa hon när jag frågade om vägbeskrivning. Jag kunde se att hennes stora glädje skulle fylla hela min dag. När min tid började ta slut var det tyvärr dags att åka hem. Vi kommer att hålla kontakt och jag ska kontakta henne direkt nästa gång jag vill resa. Jag kunde se deras intressanta kultur och det var bäst att ha öppna ögon och bara gå förbi alla vackra gamla hus längs varje väg."""

core_words = [
    "springa", "buss", "semester", "strand", "åka till", "storstad", "gå på museum", 
    "vandra", "packning", "åka på", "kompass", "besöka", "åka iväg", "resa", "stad", 
    "vara på väg", "ledighet", "sätt", "hälsa på", "komma och hälsa på", "ta slut", 
    "utomlands", "järnvägslinje", "på så sätt", "besök", "gata", "Priserna har gått upp.", 
    "ta bussen", "ta tåget", "billig", "biliotekarie", "gå ner till", "lyxhotell", 
    "busschaufför", "rida", "bil", "gå förbi", "gå ut med", "väg", "Ta samma väg som du kom.", 
    "gå iväg"
]

glue_words = [
    "veta", "bäst", "direkt", "mindre", "senare", "öppna", "spara", "snart", "fyra", 
    "klar", "rum", "fylla", "kontakta", "kort", "förstå", "kontakt", "praktisk", 
    "perfekt", "deras"
]

target_mappings = [
    ("springa", "springa"),
    ("buss", "buss"),
    ("semester", "semester"),
    ("strand", "strand"),
    ("åka till", "åka till"),
    ("storstad", "storstad"),
    ("gå på museum", "gå på museum"),
    ("vandra", "vandra"),
    ("packning", "packning"),
    ("åka på", "åka på"),
    ("kompass", "kompass"),
    ("besöka", "besöka"),
    ("åka iväg", "åka iväg"),
    ("resa", "resa"),
    ("stad", "stad"),
    ("vara på väg", "är på väg"),
    ("ledighet", "ledighet"),
    ("sätt", "sätt"),
    ("hälsa på", "hälsa på"),
    ("komma och hälsa på", "komma och hälsa på"),
    ("ta slut", "ta slut"),
    ("utomlands", "utomlands"),
    ("järnvägslinje", "järnvägslinje"),
    ("på så sätt", "På så sätt"),
    ("besök", "besök"),
    ("gata", "gata"),
    ("Priserna har gått upp.", "Priserna har gått upp."),
    ("ta bussen", "ta bussen"),
    ("ta tåget", "ta tåget"),
    ("billig", "billigt"),
    ("biliotekarie", "biliotekarie"),
    ("gå ner till", "gå ner till"),
    ("lyxhotell", "lyxhotell"),
    ("busschaufför", "busschaufför"),
    ("rida", "rida"),
    ("bil", "bil"),
    ("gå förbi", "gå förbi"),
    ("gå ut med", "gå ut med"),
    ("väg", "väg"),
    ("Ta samma väg som du kom.", "Ta samma väg som du kom."),
    ("gå iväg", "gå iväg"),

    ("veta", "veta"),
    ("bäst", "bäst"),
    ("direkt", "direkt"),
    ("mindre", "mindre"),
    ("senare", "Senare"),
    ("öppna", "öppna"),
    ("spara", "spara"),
    ("snart", "Snart"),
    ("fyra", "fyra"),
    ("klar", "klar"),
    ("rum", "rum"),
    ("fylla", "fylla"),
    ("kontakta", "kontakta"),
    ("kort", "kort"),
    ("förstå", "förstå"),
    ("kontakt", "kontakt"),
    ("praktisk", "praktiskt"),
    ("perfekt", "perfekt"),
    ("deras", "deras")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if base == "väg":
        start = text.rfind(word_in_sentence)
    elif base == "hälsa på":
        start = text.find("hälsa på henne")
    elif base == "resa":
        start = text.find("resa utomlands")
    else:
        if " " in word_in_sentence or "." in word_in_sentence:
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
    "step_id": "resor_transport",
    "step_title": "Resor & Transport",
    "article_id": "art_02",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('course/sfid/phase2/article_2.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
