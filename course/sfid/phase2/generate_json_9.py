import json
import re

text = """Att studera har blivit mer och mer viktigt för många, eftersom man ofta vill ta en examen. En skolelev i en vanlig skola får bra undervisning i ämnen som matte. För att undvika problem måste de ofta fokusera på att räkna mycket. En duktig lärare kan hjälpa till med hjälp av en bra bok. Ibland får eleverna översätta ett gammalt orspråk. En klassisk övning är att ringa in eller markera en understuken mening i texten och läsa med rätt betoning.

Jag bestämde mig för att prova en snabbkurs i pedagogik. Jag ville praktisera på en förskola för att se hur en förskollärare jobbar. Den som var yngst i vår klass var bara tjugo år, men kände sig ändå sedd. Han behövde inte be om lov för att få en bra lektion. Senare valde han att studera på universitet för att bli gymnasielärare. Man kan klassa honom som en framtida akademiker. På ett universitet kan man lära sig mycket, till och med om lyckoforskning och annan akademisk forskning. Jag vet en som vill forska om hur stress kan reducera glädjen. 

Vår rektor berättade att de skulle ta över en kurs i svenska för invandrare. Min klasskompis ville protestera mot att vi skulle ha ett stort prov senast på fredag. Han kände sig nästan lika vilsen som en björn som måste lufsa in i en bur eller stå byxlös framför alla. Men man måste prioritera och till en viss grad göra sitt bästa. Det mesta måste ju ske i tid.

Inför provet skulle vi räkna ihop poängen inom varje område och svara på en kortfattad fråga. Minst en person om året brukar få högsta betyg. Sist av alla hoppas jag att jag är bättre än någonsin på att skriva, och kanske fira med en lokalproducerad måltid."""

core_words = [
    "översätta", "bok", "studera", "examen", "undervisning", "matte", "förskollärare", 
    "gymnasielärare", "universitet", "studera på universitet", "lektion", "forskning", 
    "lyckoforskning", "forska om", "klass", "akademiker", "akademisk", "skola", 
    "rektor", "skolelev", "svenska för invandrare", "prov", "protestera", "klasskompis", 
    "klassisk", "klassa", "snabbkurs", "praktisera", "förskola", "senast på fredag", 
    "grad", "prova", "ringa in", "räkna", "område", "markera", "understuken", "räkna ihop", "betoning"
]

glue_words = [
    "fokusera på", "prioritera", "orspråk", "reducera", "en person om året", "ske", 
    "byxlös", "undvika", "eftersom", "bur", "be om lov", "lokalproducerad", "ta över", 
    "kortfattad", "sedd", "mer och mer", "någonsin", "med hjälp av", "yngst", "lufsa", "sist"
]

target_mappings = [
    # Core
    ("översätta", "översätta"),
    ("bok", "bok"),
    ("studera", "studera"),
    ("examen", "examen"),
    ("undervisning", "undervisning"),
    ("matte", "matte"),
    ("förskollärare", "förskollärare"),
    ("gymnasielärare", "gymnasielärare"),
    ("universitet", "universitet"),
    ("studera på universitet", "studera på universitet"),
    ("lektion", "lektion"),
    ("forskning", "forskning"),
    ("lyckoforskning", "lyckoforskning"),
    ("forska om", "forska om"),
    ("klass", "klass"),
    ("akademiker", "akademiker"),
    ("akademisk", "akademisk"),
    ("skola", "skola"),
    ("rektor", "rektor"),
    ("skolelev", "skolelev"),
    ("svenska för invandrare", "svenska för invandrare"),
    ("prov", "prov"),
    ("protestera", "protestera"),
    ("klasskompis", "klasskompis"),
    ("klassisk", "klassisk"),
    ("klassa", "klassa"),
    ("snabbkurs", "snabbkurs"),
    ("praktisera", "praktisera"),
    ("förskola", "förskola"),
    ("senast på fredag", "senast på fredag"),
    ("grad", "grad"),
    ("prova", "prova"),
    ("ringa in", "ringa in"),
    ("räkna", "räkna"),
    ("område", "område"),
    ("markera", "markera"),
    ("understuken", "understuken"),
    ("räkna ihop", "räkna ihop"),
    ("betoning", "betoning"),

    # Glue
    ("fokusera på", "fokusera på"),
    ("prioritera", "prioritera"),
    ("orspråk", "orspråk"),
    ("reducera", "reducera"),
    ("en person om året", "en person om året"),
    ("ske", "ske"),
    ("byxlös", "byxlös"),
    ("undvika", "undvika"),
    ("eftersom", "eftersom"),
    ("bur", "bur"),
    ("be om lov", "be om lov"),
    ("lokalproducerad", "lokalproducerad"),
    ("ta över", "ta över"),
    ("kortfattad", "kortfattad"),
    ("sedd", "sedd"),
    ("mer och mer", "mer och mer"),
    ("någonsin", "någonsin"),
    ("med hjälp av", "med hjälp av"),
    ("yngst", "yngst"),
    ("lufsa", "lufsa"),
    ("sist", "Sist")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if base == "studera":
        start = text.find("Att studera") + 4
    elif base == "universitet":
        start = text.find("ett universitet kan") + 4
    elif base == "klass":
        start = text.find("vår klass var") + 4
    elif base == "skola":
        start = text.find("vanlig skola får") + 7
    elif base == "räkna":
        start = text.find("att räkna mycket") + 4
    elif base == "forskning":
        start = text.find("akademisk forskning.") + 10
    elif base == "prov":
        start = text.find("stort prov senast") + 6
    else:
        if " " in word_in_sentence or "." in word_in_sentence or "?" in word_in_sentence or "…" in word_in_sentence:
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
    "article_id": "art_09",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('./course/sfid/phase2/article_9.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
