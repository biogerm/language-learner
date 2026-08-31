import json
import re

text = """En spännande vecka på kontoret

"Jag skriver till er för att…" började min sekreterare läsa ur ett brev. Anledningen var att en pr-konsult ville presentera ett nytt projekt. Det var ett stort byggnadsprojekt bredvid ett nytt handelscentrum. "Det blir ett spännande öde för staden," sa vår vd.

Han planerade att investera i en ny produkt. Fabriken skulle tillverka en fet lyxvara och hoppades att den skulle bli en storsäljare. För att lansera den bra behövde han bra försäljning och handel. "Du måste kontakta någon som kan hjälpa till," sa han. "Du skulle kunna prova/försöka." Jag är serviceinriktad och duktig på min arbetsuppgift.

Det var ett viktigt möte. Jag var noga med att inte komma försent, utan kom precis i rätt tid. För att förbereda sig hade han skrivit några stödord på en tavla nedanför skärmen. Ett bra knep är att använda exakt rätt titel. "Vi ska besluta om framtiden," sa han. Han ville kräva att vår personal skulle samarbeta mer. Numera måste vi också införa nya regler som har att göra med säkerhet på varje bygge.

"Vi behöver en advokat och en revisor för att skriva under avtal," sa han. "Det kan vara en tung och stressig tid. Vi kan inte dölja att arbetet kan ta en dryg månad." "Det tycker inte jag heller." sa en kommissarie som var där för säkerhetsfrågor. Vi pratade också om att anställa en apotekare på deltid och en servitris till kantinen.

"Jag tycker inte att vi ska anställa varken…eller av dem just nu," sa vd:n. "Vid ett annat tillfälle kan de få en chans." Alla som ville bli medlem i klubben fick en betald plats, och varje medlem var nöjd."""

core_words = [
    "Anledningen", "presentera", "deltid", "besluta om", "förbereda sig", 
    "Jag skriver till er för att…", "kontakta någon", "komma försent", "vd", "servitris", 
    "betald", "medlem", "duktig", "pr-konsult", "projekt", "arbetsuppgift", "tung", 
    "investera", "kräva att", "advokat", "stressig", "bli medlem", "personal", "möte", 
    "serviceinriktad", "tillverka", "produkt", "lansera", "handel", "försäljning", 
    "storsäljare", "bygge", "revisor", "apotekare", "samarbeta", "handelscentrum", 
    "byggnadsprojekt", "kommissarie", "lyxvara", "sekreterare"
]

glue_words = [
    "exakt", "numera", "skriva under", "införa", "dölja", "precis", "dryg", 
    "Det tycker inte jag heller.", "nedanför", "spännande", "titel", "fet", 
    "som har att göra med", "få en chans", "stödord", "knep", "öde", 
    "Du skulle kunna prova/försöka.", "varken…eller", "tillfälle"
]

target_mappings = [
    # Core
    ("Anledningen", "Anledningen"),
    ("presentera", "presentera"),
    ("deltid", "deltid"),
    ("besluta om", "besluta om"),
    ("förbereda sig", "förbereda sig"),
    ("Jag skriver till er för att…", "Jag skriver till er för att…"),
    ("kontakta någon", "kontakta någon"),
    ("komma försent", "komma försent"),
    ("vd", "vd"),
    ("servitris", "servitris"),
    ("betald", "betald"),
    ("medlem", "medlem"),
    ("duktig", "duktig"),
    ("pr-konsult", "pr-konsult"),
    ("projekt", "projekt"),
    ("arbetsuppgift", "arbetsuppgift"),
    ("tung", "tung"),
    ("investera", "investera"),
    ("kräva att", "kräva att"),
    ("advokat", "advokat"),
    ("stressig", "stressig"),
    ("bli medlem", "bli medlem"),
    ("personal", "personal"),
    ("möte", "möte"),
    ("serviceinriktad", "serviceinriktad"),
    ("tillverka", "tillverka"),
    ("produkt", "produkt"),
    ("lansera", "lansera"),
    ("handel", "handel"),
    ("försäljning", "försäljning"),
    ("storsäljare", "storsäljare"),
    ("bygge", "bygge"),
    ("revisor", "revisor"),
    ("apotekare", "apotekare"),
    ("samarbeta", "samarbeta"),
    ("handelscentrum", "handelscentrum"),
    ("byggnadsprojekt", "byggnadsprojekt"),
    ("kommissarie", "kommissarie"),
    ("lyxvara", "lyxvara"),
    ("sekreterare", "sekreterare"),

    # Glue
    ("exakt", "exakt"),
    ("numera", "Numera"),
    ("skriva under", "skriva under"),
    ("införa", "införa"),
    ("dölja", "dölja"),
    ("precis", "precis"),
    ("dryg", "dryg"),
    ("Det tycker inte jag heller.", "Det tycker inte jag heller."),
    ("nedanför", "nedanför"),
    ("spännande", "spännande"),
    ("titel", "titel"),
    ("fet", "fet"),
    ("som har att göra med", "som har att göra med"),
    ("få en chans", "få en chans"),
    ("stödord", "stödord"),
    ("knep", "knep"),
    ("öde", "öde"),
    ("Du skulle kunna prova/försöka.", "Du skulle kunna prova/försöka."),
    ("varken…eller", "varken…eller"),
    ("tillfälle", "tillfälle")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if base == "vd":
        start = text.find("sa vår vd.") + 7
    elif base == "medlem":
        start = text.find("varje medlem") + 6
    elif base == "projekt":
        start = text.find("nytt projekt.") + 5
    elif base == "handel":
        start = text.find("och handel.") + 4
    elif base == "spännande":
        start = text.find("spännande öde")
    else:
        if " " in word_in_sentence or "." in word_in_sentence or "?" in word_in_sentence or "…" in word_in_sentence or "/" in word_in_sentence:
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
    "step_id": "arbetsliv",
    "step_title": "Arbetsliv",
    "article_id": "art_07",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('course/sfid/phase2/article_7.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
