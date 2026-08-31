import json
import re

text = """Förr i tiden var det viktigt att kunna koka sylt och konservera mat för att ha mat under hela vintern. "Det hade jag ingen aning om." sa min vän från Spanien. För att imponera på honom bestämde jag mig för att lära honom om svensk mat. Det fanns många stora matprojekt innan vi ens började äta, som karamellkokning. Allt hände i köket och jag ville nästan uppfostra honom i vår kultur.

I vintras brukade vi baka en bulle med jäst och äta marmelad med smak av apelsin. Det var en lätt och färsk frukost. Men han ville hellre gå på restaurang för att äta en god sallad med kyckling och ägg. "Okej då." sa jag, och vi åt ute istället. 

Jag ville visa att svensk matkultur också kan förändras och vara progressiv. "Kom igen!" ropade jag. Vi gick till en marknad. Landets regerande snackstillverkare sålde en underbar blandning av bränd nöt och kanderad viol eller syren. Efter en tid valde vi att köpa en mjuk och seg gräddkola. Vi köpte också lite salt sill och en burk surströmming.

Under lång tid brukade man stanna upp på kvällen för att äta något gott. Man kunde blanda lite svamp och salta ordentligt. Man sparade allt i sitt skafferi. Idag är maten ofta producerad utomlands, och lastbilar trafikerar vägarna till och från affärerna för att ge oss färdiga varor. Det är mycket enklare nu än förr. 

Efter middagen bjöd jag på fryst glass med lite grädde, honung och lite sylt på toppen. Han älskade det. Svensk mat är fantastisk. "Är du med?" frågade jag. Han nickade instämmande och ville att jag skulle upprepa receptet, eftersom olika typer av mat fascinerade honom. En av landets största utmaningar är att bevara det gamla, men detta gick bra.

Hälsningar …
Anna"""

core_words = [
    "lära", "toppen", "gå på restaurang", "kyckling", "istället", "upprepa", 
    "trafikera", "lätt", "gott", "marmelad", "bulle", "ägg", "svamp", "koka sylt", 
    "konservera", "skafferi", "blandning", "blanda", "salta", "jäst", "apelsin", 
    "nöt", "karamellkokning", "gräddkola", "honung", "seg", "fryst", "glass", 
    "syren", "viol", "färsk", "sylt", "sill", "surströmming", "salt", "kanderad", 
    "bränd", "grädde"
]

glue_words = [
    "Hälsningar …", "regerande", "Det hade jag ingen aning om.", "stanna upp", 
    "i vintras", "innan", "olik", "störst", "snackstillverkare", "Okej då.", 
    "efter en tid", "till och från", "under lång tid", "än", "producerad", 
    "imponera", "progressiv", "Kom igen!", "förändras", "förr", "uppfostra", 
    "Är du med?"
]

target_mappings = [
    # Core
    ("lära", "lära"),
    ("toppen", "toppen"),
    ("gå på restaurang", "gå på restaurang"),
    ("kyckling", "kyckling"),
    ("istället", "istället"),
    ("upprepa", "upprepa"),
    ("trafikera", "trafikerar"),
    ("lätt", "lätt"),
    ("gott", "gott"),
    ("marmelad", "marmelad"),
    ("bulle", "bulle"),
    ("ägg", "ägg"),
    ("svamp", "svamp"),
    ("koka sylt", "koka sylt"),
    ("konservera", "konservera"),
    ("skafferi", "skafferi"),
    ("blandning", "blandning"),
    ("blanda", "blanda"),
    ("salta", "salta"),
    ("jäst", "jäst"),
    ("apelsin", "apelsin"),
    ("nöt", "nöt"),
    ("karamellkokning", "karamellkokning"),
    ("gräddkola", "gräddkola"),
    ("honung", "honung"),
    ("seg", "seg"),
    ("fryst", "fryst"),
    ("glass", "glass"),
    ("syren", "syren"),
    ("viol", "viol"),
    ("färsk", "färsk"),
    ("sylt", "sylt"),
    ("sill", "sill"),
    ("surströmming", "surströmming"),
    ("salt", "salt"),
    ("kanderad", "kanderad"),
    ("bränd", "bränd"),
    ("grädde", "grädde"),

    # Glue
    ("Hälsningar …", "Hälsningar …"),
    ("regerande", "regerande"),
    ("Det hade jag ingen aning om.", "Det hade jag ingen aning om."),
    ("stanna upp", "stanna upp"),
    ("i vintras", "I vintras"),
    ("innan", "innan"),
    ("olik", "olika"),
    ("störst", "största"),
    ("snackstillverkare", "snackstillverkare"),
    ("Okej då.", "Okej då."),
    ("efter en tid", "Efter en tid"),
    ("till och från", "till och från"),
    ("under lång tid", "Under lång tid"),
    ("än", "än"),
    ("producerad", "producerad"),
    ("imponera", "imponera"),
    ("progressiv", "progressiv"),
    ("Kom igen!", "Kom igen!"),
    ("förändras", "förändras"),
    ("förr", "Förr"),
    ("uppfostra", "uppfostra"),
    ("Är du med?", "Är du med?")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if base == "sylt":
        start = text.find("lite sylt") + 5
    elif base == "gott":
        start = text.find("något gott") + 6
    elif base == "salt":
        start = text.find("salt sill")
    elif base == "förr":
        start = text.find("Förr i tiden")
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
    "step_id": "mat_matlagning",
    "step_title": "Mat & Matlagning",
    "article_id": "art_15",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('course/sfid/phase2/article_15.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
