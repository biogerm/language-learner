import json
import re

text = """Att börja en ny utbildning för att lära sig ett nytt språk är alltid intressant. Min kurskamrat och jag bestämde oss för att gå en kurs. Innan vi började på ett univerisitet tänkte vi testa en privatlärare. Vi hade läst en undersökning från 1700-talet om hur olika grupper av människor kunde utbilda sig. Där stod att barn från överklass brukade uppfostras med egen lärare, medan arbetarklass och övrig samhällsklass inte fick samma chans. "Varför fick hon ingen…?" undrade min kompis när hon läste om en fattig flicka. 

Idag kan man utbilda sig till vad som helst. Första dagen fick vi vända sida i boken och läsa en mening. "Du måste uttala varje fras rätt," sa läraren. Hon brukade förklara grammatik, som ordföljd och varje ordklass. Vi lärde oss skillnaden mellan substantiv, adjektiv och pronomen. Vi pratade också om ett könsneutralt ord som hen. 

På lektionen måste vi skriva och svara på frågor. Läraren ville uppmana oss att skriva ner alla svarsalternativ och notera rätt svar. "Kolla i facit," sa hon, "men försök att formulera egna tankar först." Vi fick ofta i uppgift att skriva dagbok eller skriva mejl. "Vad tycker du?" frågade läraren. "Är det svårt?" Jag svarade att det förstås var lite svårt, men bra för att testa sina gränser. Det kunde nästan göra ont i huvudet av alla nya regler och man kände ibland för att bita ihop.

Ibland hade vi också en fysisk aktivitet som en danskurs efter skolan. Då kunde man se en mängd människor. Efteråt fick man gå hem och blåsa torr sitt hår. "Se upp!" sa min kompis, "Här kommer den sista bussen." När vi åkte hem sa hon: "Vem frågade efter dig?" Jag var så trött att jag kände mig stendöd, men jag orkade höra på henne ändå. Den senaste veckan var av bästa sort."""

core_words = [
    "sida", "skriva", "skriv ner", "ord", "läsa", "svara", "svar", "svarsalternativ", 
    "notera", "testa", "testa sina gränser", "adjektiv", "substantiv", "pronomen", 
    "ordklass", "mening", "förstås", "facit", "undersökning", "skriva dagbok", 
    "språk", "överklass", "samhällsklass", "arbetarklass", "kurskamrat", "förklara", 
    "grammatik", "utbilda", "utbilda sig till", "skriva mejl", "utbildning", 
    "univerisitet", "fras", "uttala", "hen", "ordföljd", "danskurs", "privatlärare", "lära sig"
]

glue_words = [
    "en mängd", "se upp!", "1700-talet", "senaste", "höra", "uppfostras", "sort", 
    "Varför fick hon ingen…?", "övrig", "fysisk", "uppmana", "Vem frågade efter dig?", 
    "sista", "stendöd", "göra ont", "blåsa torr", "könsneutral", "se", "formulera", 
    "Vad tycker du?", "bita"
]

target_mappings = [
    # Core
    ("sida", "sida"),
    ("skriva", "skriva"),
    ("skriv ner", "skriva ner"),
    ("ord", "ord"),
    ("läsa", "läsa"),
    ("svara", "svara"),
    ("svar", "svar"),
    ("svarsalternativ", "svarsalternativ"),
    ("notera", "notera"),
    ("testa", "testa"),
    ("testa sina gränser", "testa sina gränser"),
    ("adjektiv", "adjektiv"),
    ("substantiv", "substantiv"),
    ("pronomen", "pronomen"),
    ("ordklass", "ordklass"),
    ("mening", "mening"),
    ("förstås", "förstås"),
    ("facit", "facit"),
    ("undersökning", "undersökning"),
    ("skriva dagbok", "skriva dagbok"),
    ("språk", "språk"),
    ("överklass", "överklass"),
    ("samhällsklass", "samhällsklass"),
    ("arbetarklass", "arbetarklass"),
    ("kurskamrat", "kurskamrat"),
    ("förklara", "förklara"),
    ("grammatik", "grammatik"),
    ("utbilda", "utbilda"),
    ("utbilda sig till", "utbilda sig till"),
    ("skriva mejl", "skriva mejl"),
    ("utbildning", "utbildning"),
    ("univerisitet", "univerisitet"),
    ("fras", "fras"),
    ("uttala", "uttala"),
    ("hen", "hen"),
    ("ordföljd", "ordföljd"),
    ("danskurs", "danskurs"),
    ("privatlärare", "privatlärare"),
    ("lära sig", "lära sig"),

    # Glue
    ("en mängd", "en mängd"),
    ("se upp!", "Se upp!"),
    ("1700-talet", "1700-talet"),
    ("senaste", "senaste"),
    ("höra", "höra"),
    ("uppfostras", "uppfostras"),
    ("sort", "sort"),
    ("Varför fick hon ingen…?", "Varför fick hon ingen…?"),
    ("övrig", "övrig"),
    ("fysisk", "fysisk"),
    ("uppmana", "uppmana"),
    ("Vem frågade efter dig?", "Vem frågade efter dig?"),
    ("sista", "sista"),
    ("stendöd", "stendöd"),
    ("göra ont", "göra ont"),
    ("blåsa torr", "blåsa torr"),
    ("könsneutral", "könsneutralt"),
    ("se", "se"),
    ("formulera", "formulera"),
    ("Vad tycker du?", "Vad tycker du?"),
    ("bita", "bita")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if base == "skriva":
        start = text.find("måste vi skriva") + 9
    elif base == "ord":
        start = text.find("ord som hen")
    elif base == "svar":
        start = text.find("rätt svar.") + 5
    elif base == "testa":
        start = text.find("testa en privatlärare")
    elif base == "utbilda":
        start = text.find("utbilda sig. Där")
    elif base == "se":
        start = text.find("se en mängd")
    else:
        if " " in word_in_sentence or "." in word_in_sentence or "?" in word_in_sentence or "…" in word_in_sentence or "!" in word_in_sentence or "-" in word_in_sentence:
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
    "step_id": "utbildning",
    "step_title": "Utbildning",
    "article_id": "art_08",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('course/sfid/phase2/article_8.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
