import json
import re

text = """Visste du att…? Våren är min favoritårstid, särskilt under en storhelg som påsk. Jo, det är sant! Under senare delen av… ja, våren, brukar jag ofta chilla. "Brukar du mysa?" frågade mitt syskon mig nyligen. Jag svarade ja, jag älskar mys, och jag älskar att mysa. Jag gillar att ligga kvar i min mjuka pyjamas i min stora soffa, eller i en bekväm fåtölj, med en intressant damtidning bredvid mig. 

Men på många ställen i stan gillar folk att gå ut på en barrunda. Det är en rolig variant av underhållning. Någon kanske vill flytta ut strax utanför centrum för att få lite lugn, medan andra vill vara mitt i stan. "Jag har inte ett öre." sa min kompis häromdagen. Han var helt pank. Han sa att han fick panta varje tomsflaska och plocka ihop varje småsak ur sitt skåp för att klara sig. Hans veckopeng var helt slut. 

Jag ville inte hålla hemlig min egen ekonomi, så jag sa att jag måste tänka på varje grej jag köper. För att spara pengar tog jag ett klokt beslut: jag ska inte renovera mitt gamla kök nu. Det är bara viktigt att täcka mina basbehov, allt annat räknas inte just nu. Jag är inte lika flitig som en myra längre. 

Istället vill jag ta hand om mig själv. Du måste också lära dig att ta hand om dig själv. Man måste vara beredd på förändring i livet. När jag kom till min lokala kiosk kände jag att det började lukta gott av godis och kaffe. Jag köpte en pappersstrut med karameller och ett tuggummi och gick sedan till en kassa. Jag betalade och lade varorna i min väska. Sedan ställde jag mig i en rad för att vänta på bussen. "Det var hemskt trevligt." sa jag till föraren när jag klev på.

När jag kom hem ville jag ändra inredningen lite. Jag ville slå upp fönstren och låta frisk vårluft strömma in i rummet. Jag kunde peka på en vacker nyans på väggen och jämföra färgerna med min nya matta. Mitt hem är en helig plats för mig. Nästa vecka kanske en god vän ska titta förbi."""

core_words = [
    "dig själv", "bredvid", "lukta", "titta förbi", "småsak", "veckopeng", 
    "soffa", "ligga kvar", "bekväm", "flytta ut", "väska", "strax utanför", 
    "mys", "kök", "panta", "fåtölj", "basbehov", "grej", "tomsflaska", "mysa", 
    "Brukar du mysa?", "damtidning", "skåp", "renovera", "stan", "syskon", 
    "pyjamas", "peka på", "storhelg", "barrunda", "plocka ihop", "kassa", 
    "pank", "tuggummi", "pappersstrut", "kiosk", "chilla", "påsk"
]

glue_words = [
    "men", "beslut", "strömma", "Jag har inte ett öre.", "vara beredd", 
    "helig", "Det var hemskt trevligt.", "flitig som en myra", "jämföra", 
    "Visste du att…?", "räknas", "nyans", "under senare delen av…", 
    "variant av", "rad", "bruka", "ändra", "jo", "någon", "hålla hemlig", 
    "på många ställen", "slå upp"
]

target_mappings = [
    # Core
    ("dig själv", "dig själv"),
    ("bredvid", "bredvid"),
    ("lukta", "lukta"),
    ("titta förbi", "titta förbi"),
    ("småsak", "småsak"),
    ("veckopeng", "veckopeng"),
    ("soffa", "soffa"),
    ("ligga kvar", "ligga kvar"),
    ("bekväm", "bekväm"),
    ("flytta ut", "flytta ut"),
    ("väska", "väska"),
    ("strax utanför", "strax utanför"),
    ("mys", "mys"),
    ("kök", "kök"),
    ("panta", "panta"),
    ("fåtölj", "fåtölj"),
    ("basbehov", "basbehov"),
    ("grej", "grej"),
    ("tomsflaska", "tomsflaska"),
    ("mysa", "mysa"),
    ("Brukar du mysa?", "Brukar du mysa?"),
    ("damtidning", "damtidning"),
    ("skåp", "skåp"),
    ("renovera", "renovera"),
    ("stan", "stan"),
    ("syskon", "syskon"),
    ("pyjamas", "pyjamas"),
    ("peka på", "peka på"),
    ("storhelg", "storhelg"),
    ("barrunda", "barrunda"),
    ("plocka ihop", "plocka ihop"),
    ("kassa", "kassa"),
    ("pank", "pank"),
    ("tuggummi", "tuggummi"),
    ("pappersstrut", "pappersstrut"),
    ("kiosk", "kiosk"),
    ("chilla", "chilla"),
    ("påsk", "påsk"),

    # Glue
    ("men", "Men"),
    ("beslut", "beslut"),
    ("strömma", "strömma"),
    ("Jag har inte ett öre.", "Jag har inte ett öre."),
    ("vara beredd", "vara beredd"),
    ("helig", "helig"),
    ("Det var hemskt trevligt.", "Det var hemskt trevligt."),
    ("flitig som en myra", "flitig som en myra"),
    ("jämföra", "jämföra"),
    ("Visste du att…?", "Visste du att…?"),
    ("räknas", "räknas"),
    ("nyans", "nyans"),
    ("under senare delen av…", "Under senare delen av…"),
    ("variant av", "variant av"),
    ("rad", "rad"),
    ("bruka", "brukar"),
    ("ändra", "ändra"),
    ("jo", "Jo"),
    ("någon", "Någon"),
    ("hålla hemlig", "hålla hemlig"),
    ("på många ställen", "på många ställen"),
    ("slå upp", "slå upp")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if base == "dig själv":
        start = text.find("ta hand om dig själv") + 11
    elif base == "mys":
        start = text.find("älskar mys") + 7
    elif base == "men":
        start = text.find("Men ")
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
    "step_id": "vardagsliv",
    "step_title": "Vardagsliv",
    "article_id": "art_33",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('course/sfid/phase2/article_33.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
