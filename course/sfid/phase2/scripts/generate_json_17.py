import json
import re

text = """"Vad gjorde jag igår?" frågade jag i ett litet brev. "Vet du vad jag gjorde igår…?"
Igår bestämde jag mig för att utforska vår vackra natur. Jag lämnade min villaträdgård och min vanliga trädgård bakom mig. Där fanns en vacker ros med röda rosenblad som doftade underbart, men jag ville ut. Jag är mycket intresserad av vår miljö och ett folkligt friluftsliv.

"Vilken särskild händelse fick dig att åka iväg?" undrade min vän.
Jo, jag kände mig missnöjd med att bara sitta hemma. För att få ny energi, började jag att gå ut med hunden. Jag köpte en fräsig jacka och vi åkte norrut. Vi gick en lång sträcka upp på ett fjäll, där det fortfarande fanns lite snö. 

I naturen kan man uppleva mycket. En katt eller en hund är ett bra sällskpasdjur och husdjur, men att se vilda djur i en skog är bättre än i en djurpark. Där fanns hundratals små djur, bland andra ett litet rådjur och en sjungande fågel. Jag såg också en stor fjäril, vackrare än någon i en gammal fjärilssamling.

Jag fick ställa mig vid ett stort träd, som var en gammal björk, och såg gul kåda. Tyvärr måste man ofta hyra plats i andrahand på en ful parkering, ibland byggd på order av en politiker. Naturen är inte längre lika fri. Vår vackra sjö bredvid ett stort hav är nästan helt utfiskad på fisk på grund av all förorening. Det är en svår situation som ibland känns som om den började på medeltiden, och nästa generation måste efterträda oss och göra det bättre.

Vid dagens slut såg jag en magisk solnedgång och tänkte på rymden och en ljus måne. Det var lika dramatiskt som en karaktär i en klassisk Strindbergspjäs. En hemgjord saft värmde mig. "Missa inte nästa soluppgång," sa jag till mig själv. Det är viktigt att barn får växa upp i en frisk värld utan en stor grop av sopor."""

core_words = [
    "fjäll", "fjäril", "fjärilssamling", "friluftsliv", "husdjur", "trädgård", "ros", 
    "rosenblad", "snö", "rymden", "solnedgång", "hav", "soluppgång", "sjö", 
    "missnöjd", "djur", "sällskpasdjur", "hund", "fågel", "katt", "fisk", "skog", 
    "träd", "vilda djur", "rådjur", "hundratals", "djurpark", "hemgjord", 
    "villaträdgård", "miljö", "Vad gjorde jag igår?", "Vet du vad jag gjorde igår…?", 
    "Strindbergspjäs", "gå ut med hunden", "kåda", "björk", "efterträda", 
    "parkering", "måne", "utfiskad", "förorening"
]

glue_words = [
    "brev", "inte längre", "missa inte", "viktig", "grop", "bland andra", 
    "sträcka", "folklig", "fräsig", "händelse", "ställa sig", "karaktär", 
    "medeltiden", "svår", "på order av", "Vilken", "andrahand", "växa upp", "särskild"
]

target_mappings = [
    # Core
    ("fjäll", "fjäll"),
    ("fjäril", "fjäril"),
    ("fjärilssamling", "fjärilssamling"),
    ("friluftsliv", "friluftsliv"),
    ("husdjur", "husdjur"),
    ("trädgård", "trädgård"),
    ("ros", "ros"),
    ("rosenblad", "rosenblad"),
    ("snö", "snö"),
    ("rymden", "rymden"),
    ("solnedgång", "solnedgång"),
    ("hav", "hav"),
    ("soluppgång", "soluppgång"),
    ("sjö", "sjö"),
    ("missnöjd", "missnöjd"),
    ("djur", "djur"),
    ("sällskpasdjur", "sällskpasdjur"),
    ("hund", "hund"),
    ("fågel", "fågel"),
    ("katt", "katt"),
    ("fisk", "fisk"),
    ("skog", "skog"),
    ("träd", "träd"),
    ("vilda djur", "vilda djur"),
    ("rådjur", "rådjur"),
    ("hundratals", "hundratals"),
    ("djurpark", "djurpark"),
    ("hemgjord", "hemgjord"),
    ("villaträdgård", "villaträdgård"),
    ("miljö", "miljö"),
    ("Vad gjorde jag igår?", "Vad gjorde jag igår?"),
    ("Vet du vad jag gjorde igår…?", "Vet du vad jag gjorde igår…?"),
    ("Strindbergspjäs", "Strindbergspjäs"),
    ("gå ut med hunden", "gå ut med hunden"),
    ("kåda", "kåda"),
    ("björk", "björk"),
    ("efterträda", "efterträda"),
    ("parkering", "parkering"),
    ("måne", "måne"),
    ("utfiskad", "utfiskad"),
    ("förorening", "förorening"),

    # Glue
    ("brev", "brev"),
    ("inte längre", "inte längre"),
    ("missa inte", "Missa inte"),
    ("viktig", "viktigt"),
    ("grop", "grop"),
    ("bland andra", "bland andra"),
    ("sträcka", "sträcka"),
    ("folklig", "folkligt"),
    ("fräsig", "fräsig"),
    ("händelse", "händelse"),
    ("ställa sig", "ställa mig"),
    ("karaktär", "karaktär"),
    ("medeltiden", "medeltiden"),
    ("svår", "svår"),
    ("på order av", "på order av"),
    ("Vilken", "Vilken"),
    ("andrahand", "andrahand"),
    ("växa upp", "växa upp"),
    ("särskild", "särskild")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if base == "katt":
        start = text.find("En katt") + 3
    elif base == "hund":
        start = text.find("en hund") + 3
    elif base == "djur":
        start = text.find("små djur") + 4
    elif base == "fisk":
        start = text.find("på fisk") + 3
    elif base == "trädgård":
        start = text.find("vanliga trädgård") + 8
    elif base == "fjäril":
        start = text.find("stor fjäril") + 5
    elif " " in word_in_sentence or "." in word_in_sentence or "?" in word_in_sentence or "!" in word_in_sentence or "…" in word_in_sentence:
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
    "article_id": "art_17",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('course/sfid/phase2/article_17.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
