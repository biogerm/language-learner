import json
import re

text = """Sverige är en parlamentarisk demokrati med en lång historia. Tidigare hade man en stark kungamakt. Idag har monarkin ingen politisk makt. Vår statschef är en kung eller en drottning, men det är en statsminister och vår riksdag som beslutar om varje lag och styr vår stat. En blivande kronprinsessa, en prins eller en prinsessa har ett välkomnande leende men stiftar inga lagar. 

"Ska vi…?" frågade en vän plötsligt, när vi stod vid en stor järnvägsstation för att pricka in ett tåg. "Prata om aktuell politik, menar jag." 
Han var en ambitiös klättrare inom en stor borgerlig organisation. Han ville få tag på en roll som en viktig ledare och känd politiker. 
"Okej, Varifrån?" frågade jag. "Var ska vi börja?" 
"Jo, vi kan återberätta en plötslig skandal," föreslog han. "Någon ville låna ut mycket statlig valuta till en rik affärsman så han blev rik som ett troll. Det orsakade en ekonomisk kris, ett dåligt resultat av fel värdering."

Vi pratade också om mörkare händelser i vårt samhälle. Förr i tiden kunde en elit utföra en maktdemonstration. Då kunde hemskheter hända, till och med ett mord. Någon kunde mörda sin konkurrent. Idag har vi en bra polis som ska stå för säkerheten. Det är viktigt att varje judisk, muslimsk eller kristen grupp ska känna sig trygg. I en modern kyrka ska man kunna fira en religiös gudstjänst i fred. En laglig rättighet och en rättvis regel skapar möjligheter av olika slag, vilket ger en bättre livskvalitet för alla.

Medan vi pratade satt en söt liten valp på marken och gnydde. En flicka försökte trösta hunden eftersom den hade blivit skrämd av en högljudd hårtork inifrån en frisersalong. Jag började klappa i händerna för att locka på hunden. Det är roligt hur man ibland kan tröttna på samhällsproblem och istället prata om svensk grammatik. 
"I svenskan finns det något som kallas partikelverb," sa min vän. "Man kombinerar ett verb med en partikel. Du kan också använda ett presens particip."
Jag suckade. Vi behövde hitta en bra avslutningsfras för att sluta samtalet innan tåget rullade in."""

core_words = [
    "historia", "stat", "regel", "gudstjänst", "religiös", "lag", 
    "drottning", "riksdag", "organisation", "kyrka", "polis", 
    "skandal", "ekonomisk", "judisk", "borgerlig", "mörda", "politik", 
    "mord", "laglig", "politiker", "ledare", "livskvalitet", "trösta", 
    "maktdemonstration", "valp", "partikelverb", "partikel", 
    "presens particip", "av olika slag", "valuta", "järnvägsstation", 
    "prins", "prinsessa", "statsminister", "parlamentarisk", "demokrati", 
    "statschef", "makt", "kungamakt", "kronprinsessa"
]

glue_words = [
    "aktuell", "Ska vi…?", "avslutningsfras", "resultat av", "få tag på", 
    "rik som ett troll", "plötslig", "välkomnande", "värdering", 
    "klättrare", "pricka in", "på marken", "låna ut", "stå för", "hårtork", 
    "hända", "klappa i händerna", "tröttna", "varifrån?", "återberätta"
]

target_mappings = [
    # Core
    ("historia", "historia"),
    ("stat", "stat"),
    ("regel", "regel"),
    ("gudstjänst", "gudstjänst"),
    ("religiös", "religiös"),
    ("lag", "lag"),
    ("drottning", "drottning"),
    ("riksdag", "riksdag"),
    ("organisation", "organisation"),
    ("kyrka", "kyrka"),
    ("polis", "polis"),
    ("skandal", "skandal"),
    ("ekonomisk", "ekonomisk"),
    ("judisk", "judisk"),
    ("borgerlig", "borgerlig"),
    ("mörda", "mörda"),
    ("politik", "politik"),
    ("mord", "mord"),
    ("laglig", "laglig"),
    ("politiker", "politiker"),
    ("ledare", "ledare"),
    ("livskvalitet", "livskvalitet"),
    ("trösta", "trösta"),
    ("maktdemonstration", "maktdemonstration"),
    ("valp", "valp"),
    ("partikelverb", "partikelverb"),
    ("partikel", "partikel"),
    ("presens particip", "presens particip"),
    ("av olika slag", "av olika slag"),
    ("valuta", "valuta"),
    ("järnvägsstation", "järnvägsstation"),
    ("prins", "prins"),
    ("prinsessa", "prinsessa"),
    ("statsminister", "statsminister"),
    ("parlamentarisk", "parlamentarisk"),
    ("demokrati", "demokrati"),
    ("statschef", "statschef"),
    ("makt", "makt"),
    ("kungamakt", "kungamakt"),
    ("kronprinsessa", "kronprinsessa"),

    # Glue
    ("aktuell", "aktuell"),
    ("Ska vi…?", "Ska vi…?"),
    ("avslutningsfras", "avslutningsfras"),
    ("resultat av", "resultat av"),
    ("få tag på", "få tag på"),
    ("rik som ett troll", "rik som ett troll"),
    ("plötslig", "plötslig"),
    ("välkomnande", "välkomnande"),
    ("värdering", "värdering"),
    ("klättrare", "klättrare"),
    ("pricka in", "pricka in"),
    ("på marken", "på marken"),
    ("låna ut", "låna ut"),
    ("stå för", "stå för"),
    ("hårtork", "hårtork"),
    ("hända", "hända"),
    ("klappa i händerna", "klappa i händerna"),
    ("tröttna", "tröttna"),
    ("varifrån?", "Varifrån?"),
    ("återberätta", "återberätta")
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
    "article_id": "art_42",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('./course/sfid/phase2/article_42.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
