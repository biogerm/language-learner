import json
import re

text = """Min vän och jag hade lagat middag tillsammans. Medan vi höll på med vår matlagning i ett chockrosa kök, började vi diskutera hur vårt samhälle har förändrats. Vi var givetvis lite trötta, men också glada över ett trevligt mottagande från gästerna tidigare.

"Vad tänker du på?" frågade min vän, som alltid är väldigt open-minded i sina åsikter.
"Jag tänker på hur det var historiskt sett," sa jag. "Under frihetstiden och tidigare fick varje kvinna och oskyldig människa lida när landets armé tvingades ut för att kriga och försvara ett stort rike."

"Det är sant. En medveten majoritet av folket, eller snarare en stor del av vår folkmängd, drabbades ofta när gamla kungar skulle dra streck på kartan och bestämma över landets tronföljd. Men det var ännu värre för en utländsk minoritet," sa hon. "Är vi lyckligare idag?"

"Det beror på." sa jag. "Många tycker att det blivit mycket bättre. Efter en lång historisk process och en snabb industrialisering såg vi en industriell tillväxt växa fram. Vi fick en europeisk utveckling som gav fler och fler människor stabilitet."

Vi pratade också om lag och rätt. Idag har vi ett modernt institut för juridik och en rättvis domare som kan döma om någon skulle begå ett brott. Förr i tiden var man ofta helt omedveten om sina rättigheter, och ett straff delades snabbt ut, medan en belöning bara gick till makteliten. "Jaha, då ska vi se …" sa min vän ironiskt. "Dagens makthavare försöker åtminstone publicera sina beslut." 

"På tal om skyldigheter, har du skickat in din deklaration?" frågade jag.
"Nej, jag måste deklarera imorgon," svarade hon. "Men jag måste varna för att prata mer om staten. Jag känner att jag tagit en… för mycket av vinet." 

Vi bytte ämne. "Vad fick ni?" frågade jag plötsligt, och syftade på en tävling. Hon hade fått nio poäng. Vi pratade även om en tidigare resa. "En snäll schweizare erbjöd oss lift när vi reste söderut nära den norska gränsen," berättade hon. "Senare bodde vi i en stuga på landet."

Vi diskuterade sedan vad som händer efter livet. "Tror du på reinkarnation?" frågade hon. "Att man föds igen efteråt?"
"Jag blev lite skrämd av den tanken," sa jag, "men till slut insåg jag att det är fascinerande. Mer än en hälft av jordens befolkning tror på något sådant, medan resten av dem föredrar att hävda något annat. Det finns dock inga bevis just nu."

När två bråkiga katter plötsligt började slåss i hallen, fick jag gå emellan och dela ut lite mat för att lugna dem. Min vän ville genast följa med ut och hjälpa till."""

core_words = [
    "samhälle", "tronföljd", "matlagning", "chockrosa", "söderut", 
    "kriga", "historiskt sett", "frihetstiden", "juridik", "rike", 
    "Vad tänker du på?", "reinkarnation", "varna för", "lift", 
    "minoritet", "Jaha, då ska vi se …", "deklaration", "deklarera", 
    "omedveten", "belöning", "straff", "efteråt", "skrämd", 
    "folkmängd", "publicera", "medveten", "begå", "armé", "domare", 
    "kvinna", "industriell", "historisk", "schweizare", "växa fram", 
    "gå emellan", "industrialisering", "europeisk", "människa", 
    "majoritet", "institut"
]

glue_words = [
    "dock", "Det beror på.", "nio", "givetvis", "till slut", 
    "mottagande", "Vad fick ni?", "fler och fler", "bättre", 
    "följa med", "på landet", "hävda", "norska gränsen", "just nu", 
    "hälft", "dela ut", "resten av", "minded", "dra streck", "en… för mycket"
]

target_mappings = [
    # Core
    ("samhälle", "samhälle"),
    ("tronföljd", "tronföljd"),
    ("matlagning", "matlagning"),
    ("chockrosa", "chockrosa"),
    ("söderut", "söderut"),
    ("kriga", "kriga"),
    ("historiskt sett", "historiskt sett"),
    ("frihetstiden", "frihetstiden"),
    ("juridik", "juridik"),
    ("rike", "rike"),
    ("Vad tänker du på?", "Vad tänker du på?"),
    ("reinkarnation", "reinkarnation"),
    ("varna för", "varna för"),
    ("lift", "lift"),
    ("minoritet", "minoritet"),
    ("Jaha, då ska vi se …", "Jaha, då ska vi se …"),
    ("deklaration", "deklaration"),
    ("deklarera", "deklarera"),
    ("omedveten", "omedveten"),
    ("belöning", "belöning"),
    ("straff", "straff"),
    ("efteråt", "efteråt"),
    ("skrämd", "skrämd"),
    ("folkmängd", "folkmängd"),
    ("publicera", "publicera"),
    ("medveten", "medveten"),
    ("begå", "begå"),
    ("armé", "armé"),
    ("domare", "domare"),
    ("kvinna", "kvinna"),
    ("industriell", "industriell"),
    ("historisk", "historisk"),
    ("schweizare", "schweizare"),
    ("växa fram", "växa fram"),
    ("gå emellan", "gå emellan"),
    ("industrialisering", "industrialisering"),
    ("europeisk", "europeisk"),
    ("människa", "människa"),
    ("majoritet", "majoritet"),
    ("institut", "institut"),

    # Glue
    ("dock", "dock"),
    ("Det beror på.", "Det beror på."),
    ("nio", "nio"),
    ("givetvis", "givetvis"),
    ("till slut", "till slut"),
    ("mottagande", "mottagande"),
    ("Vad fick ni?", "Vad fick ni?"),
    ("fler och fler", "fler och fler"),
    ("bättre", "bättre"),
    ("följa med", "följa med"),
    ("på landet", "på landet"),
    ("hävda", "hävda"),
    ("norska gränsen", "norska gränsen"),
    ("just nu", "just nu"),
    ("hälft", "hälft"),
    ("dela ut", "dela ut"),
    ("resten av", "resten av"),
    ("minded", "minded"),
    ("dra streck", "dra streck"),
    ("en… för mycket", "en… för mycket")
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
    "step_id": "samhälle_politik",
    "step_title": "Samhälle & Politik",
    "article_id": "art_45",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('course/sfid/phase2/article_45.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
