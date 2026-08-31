import json
import re

text = """Jag studerar ett nytt ämne på en spännande folkhögskola i staden. Varje dag har vi en föreläsning om olika historiska språk, och förra veckan lärde vi oss mycket om den indoeuropeiska språkfamiljen. I den familjen är det välkänt att germanska språk som urnordiska, isländska och färöiska ingår. Även om de är besläktade, och har liknande grammatik, låter de ofta väldigt olika när de talas. Andra kända språk i Europa som estniska, samiska och ungerska tillhör nämligen den finsk-ugriska familjen. Dessutom talade vi om inuitspråk på Grönland och hur en rysk dialekt kan påverka en hel grupp av människor i gränsområden. "Kommer du ihåg?" frågade en äldre dam i min klass när vi diskuterade. "Läraren sa att det finns en giantisk summa språk i världen, över sex tusen totalt!" 

Vi fick därefter i uppgift att skriva en artikel om grammatik. Läraren sa att vi skulle välja en röd rubrik och skriva en bra inledning för att locka läsaren. Förutom det måste vi följa en kursiverad språkkonvention för alla exempelord. Ett råd var att "Säga något högt" när man skriver. Vi skulle nämligen redovisa allt detta skriftligt inför hela klassen. För att göra det tydligare: man kan till exempel… sätta ett sammansatt ord inom parentes för att förklara dess betydelse. "Har du provat/försökt att…?" frågade läraren när jag verkade osäker. Hon gav mig mycket stöd.

I vår text skulle vi framförallt visa att vi förstår grundläggande grammatik. Vi fyllde noggrant en kolumn i boken med verb i infinitiv, presens och preteritum. Vi lärde oss också att böja varje verbgrupp i rätt tempus, som till exempel konditionalis, vilket kan vara ganska svårt för många. En komplett verbfras är viktig, precis som att använda bra sambandsord och förstå hur direkt och indirekt tal fungerar i dialoger. Vi lärde oss även skillnaden mellan vad som är en kort stavelse och en lång stavelse när man pratar. Vi fick i uppdrag att meddela varandra omedelbart om vi såg en felaktig genetivform eller ett adjektiv i superlativ.

Slutligen berättade läraren om hur nuvarande och samtida regler ständigt har utvecklats genom åren. Svenska akademien arbetar mycket aktivt för att möta nya behov i samhället. Ett politiskt beslut eller en negativ debatt mot vissa förändringar påverkar också hur språket växer. Nya ord kan ständigt födas ur vardagen, medan andra kan falla bort, nästan på samma sätt som gamla kläder säljs på extrapris. Det kändes otroligt bra när texten slutligen blev helt färdig efter allt hårt arbete."""

core_words = [
    "rubrik", "artikel", "verbfras", "lång stavelse", "kort stavelse", "inledning", 
    "sambandsord", "presens", "kolumn", "verbgrupp", "infinitiv", "indirekt tal", 
    "preteritum", "inom parentes", "redovisa", "genetivform", "ämne", "konditionalis", 
    "tempus", "superlativ", "finsk-ugriska", "föreläsning", "inuitspråk", "folkhögskola", 
    "kursiverad", "urnordiska", "estniska", "Svenska akademien", "färöiska", "germanska", 
    "indoeuropeiska", "isländska", "samiska", "ungerska", "sammansatt", "språkkonvention", "rysk"
]

glue_words = [
    "nuvarande", "dam", "summa", "Säga något högt", "födas", "falla", "färdig", "meddela", 
    "man kan till exempel…", "samtida", "Kommer du ihåg?", "giantisk", "negativ", "extrapris", 
    "mot", "röd", "nämligen", "politisk", "även om", "förutom", "grupp", "Har du provat/försökt att…?", "möta"
]

target_mappings = [
    # Core
    ("rubrik", "rubrik"),
    ("artikel", "artikel"),
    ("verbfras", "verbfras"),
    ("lång stavelse", "lång stavelse"),
    ("kort stavelse", "kort stavelse"),
    ("inledning", "inledning"),
    ("sambandsord", "sambandsord"),
    ("presens", "presens"),
    ("kolumn", "kolumn"),
    ("verbgrupp", "verbgrupp"),
    ("infinitiv", "infinitiv"),
    ("indirekt tal", "indirekt tal"),
    ("preteritum", "preteritum"),
    ("inom parentes", "inom parentes"),
    ("redovisa", "redovisa"),
    ("genetivform", "genetivform"),
    ("ämne", "ämne"),
    ("konditionalis", "konditionalis"),
    ("tempus", "tempus"),
    ("superlativ", "superlativ"),
    ("finsk-ugriska", "finsk-ugriska"),
    ("föreläsning", "föreläsning"),
    ("inuitspråk", "inuitspråk"),
    ("folkhögskola", "folkhögskola"),
    ("kursiverad", "kursiverad"),
    ("urnordiska", "urnordiska"),
    ("estniska", "estniska"),
    ("Svenska akademien", "Svenska akademien"),
    ("färöiska", "färöiska"),
    ("germanska", "germanska"),
    ("indoeuropeiska", "indoeuropeiska"),
    ("isländska", "isländska"),
    ("samiska", "samiska"),
    ("ungerska", "ungerska"),
    ("sammansatt", "sammansatt"),
    ("språkkonvention", "språkkonvention"),
    ("rysk", "rysk"),

    # Glue
    ("nuvarande", "nuvarande"),
    ("dam", "dam"),
    ("summa", "summa"),
    ("Säga något högt", "Säga något högt"),
    ("födas", "födas"),
    ("falla", "falla"),
    ("färdig", "färdig"),
    ("meddela", "meddela"),
    ("man kan till exempel…", "man kan till exempel…"),
    ("samtida", "samtida"),
    ("Kommer du ihåg?", "Kommer du ihåg?"),
    ("giantisk", "giantisk"),
    ("negativ", "negativ"),
    ("extrapris", "extrapris"),
    ("mot", "mot"),
    ("röd", "röd"),
    ("nämligen", "nämligen"),
    ("politisk", "politiskt"),
    ("även om", "Även om"),
    ("förutom", "Förutom"),
    ("grupp", "grupp"),
    ("Har du provat/försökt att…?", "Har du provat/försökt att…?"),
    ("möta", "möta")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if base == "mot":
        start = text.find("mot vissa")
    elif base == "grupp":
        start = text.find("grupp av")
    elif base == "dam":
        start = text.find("dam i")
    elif base == "rysk":
        start = text.find("rysk dialekt")
    elif base == "Svenska akademien":
        start = text.find("Svenska akademien")
    elif " " in word_in_sentence or "." in word_in_sentence or "?" in word_in_sentence or "…" in word_in_sentence or "-" in word_in_sentence or "/" in word_in_sentence:
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
    "step_id": "utbildning",
    "step_title": "Utbildning",
    "article_id": "art_11",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('course/sfid/phase2/article_11.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
