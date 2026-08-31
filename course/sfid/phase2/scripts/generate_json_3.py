import json
import re

text = """"Vad hände igår?" frågade min vän, som var väldigt ressugen. "Vet du vad som hände igår?" frågade hon sedan snabbt. Jag svarade att det var en lång historia. Vi hade bestämt oss för att bila i en stor, fin och snabb ferraribil som skulle gå i arv från min farbror. Vår plan var att campa året runt och se hela landet. Den svenska turistnäring är stark, och varje turist kan få hjälp på en lokal turisinformation.

Vi började vår resa med en långpromenad i en vacker skärgård. Där fanns det många små öar som kunde bilda grunden för en fantastisk upplevelse. Mellan öarna fanns det vatten, och vi fick använda en roddbåt för att ta sig runt i en liten hamn. Där fanns en bra och stabil brygga. Två män talade med oss och ville guida oss på en guidad tur. De berättade att bergen började resa sig ur havet. Det kunde bli mörkt, men allt var mycket vackert. Men plötsligt kom en björn ut ur skogen och verkade gå till attack, fast den egentligen bara var rädd. "Björnar brukar gå i ide på vintern," sa guiden och lugnade oss.

På söndagen tog vi en lugn söndagspromenad på en gammal stig. Där fick vi ett flygblad från en ung gatuförsäljare. Texten på bladet handlade om en stor kappsegling och om hur man kan bilda team med andra människor. "Vet du när bussarna går?" frågade min vän, eftersom vi var trötta på att promenera och ville köra på nästa cykelbana för att se staden Tain i Skottland. Jag vet att det är långt dit, men drömmar är fria. Vår packning började väga mycket. Vi ville åka ur skogen, så vi bestämde oss för att vi skulle åka dit en annan gång.

Nu är det vinter och det finns vägsalt på varje vinterväg, vilket är ett måste enligt vår grundlag för säkerhet. Det kan vara en läskig upplevelse att köra när det är halt. Båda mina vänner är hemma nu, och vi är redo att ge oss ut på nya äventyr under nästa ledighet. Att röra på sig är alltid bra. Vem vet vart vi ska gå nästa gång?"""

core_words = [
    "skärgård", "resa sig", "bilda", "vägsalt", "väga", "gå i ide", "bilda grunden för", "vinterväg", 
    "gå till attack", "Vet du när bussarna går?", "Vad hände igår?", "en annan gång", "långpromenad", 
    "Vet du vad som hände igår?", "ressugen", "ferraribil", "gatuförsäljare", "söndagspromenad", "turist", 
    "gå i arv", "köra på", "flygblad", "stabil", "åka ur", "cykelbana", "grundlag", "bila", "läskig", 
    "stig", "turistnäring", "turisinformation", "campa", "tain", "kappsegling", "guida", "guidad tur", 
    "året runt", "ta sig runt", "promenera", "hamn", "roddbåt"
]

glue_words = [
    "bra", "nu", "andra", "bli", "båda", "tala", "sedan", "under", "ge", "röra", "två", 
    "vem", "många", "gå", "mellan", "använda", "snabb", "stark", "fin"
]

target_mappings = [
    # Core
    ("skärgård", "skärgård"),
    ("resa sig", "resa sig"),
    ("bilda", "bilda"),
    ("vägsalt", "vägsalt"),
    ("väga", "väga"),
    ("gå i ide", "gå i ide"),
    ("bilda grunden för", "bilda grunden för"),
    ("vinterväg", "vinterväg"),
    ("gå till attack", "gå till attack"),
    ("Vet du när bussarna går?", "Vet du när bussarna går?"),
    ("Vad hände igår?", "Vad hände igår?"),
    ("en annan gång", "en annan gång"),
    ("långpromenad", "långpromenad"),
    ("Vet du vad som hände igår?", "Vet du vad som hände igår?"),
    ("ressugen", "ressugen"),
    ("ferraribil", "ferraribil"),
    ("gatuförsäljare", "gatuförsäljare"),
    ("söndagspromenad", "söndagspromenad"),
    ("turist", "turist"),
    ("gå i arv", "gå i arv"),
    ("köra på", "köra på"),
    ("flygblad", "flygblad"),
    ("stabil", "stabil"),
    ("åka ur", "åka ur"),
    ("cykelbana", "cykelbana"),
    ("grundlag", "grundlag"),
    ("bila", "bila"),
    ("läskig", "läskig"),
    ("stig", "stig"),
    ("turistnäring", "turistnäring"),
    ("turisinformation", "turisinformation"),
    ("campa", "campa"),
    ("tain", "Tain"),
    ("kappsegling", "kappsegling"),
    ("guida", "guida"),
    ("guidad tur", "guidad tur"),
    ("året runt", "året runt"),
    ("ta sig runt", "ta sig runt"),
    ("promenera", "promenera"),
    ("hamn", "hamn"),
    ("roddbåt", "roddbåt"),
    
    # Glue
    ("bra", "bra"),
    ("nu", "Nu"),
    ("andra", "andra"),
    ("bli", "bli"),
    ("båda", "Båda"),
    ("tala", "talade"),
    ("sedan", "sedan"),
    ("under", "under"),
    ("ge", "ge"),
    ("röra", "röra"),
    ("två", "Två"),
    ("vem", "Vem"),
    ("många", "många"),
    ("gå", "gå"),
    ("mellan", "Mellan"),
    ("använda", "använda"),
    ("snabb", "snabb"),
    ("stark", "stark"),
    ("fin", "fin")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if base == "bilda":
        start = text.find("bilda team")
    elif base == "gå":
        start = text.find("gå nästa gång")
    elif base == "Vad hände igår?":
        start = text.find("Vad hände igår?")
    else:
        if " " in word_in_sentence or "." in word_in_sentence or "?" in word_in_sentence:
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
    "article_id": "art_03",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('course/sfid/phase2/article_3.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
