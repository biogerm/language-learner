import json
import re

text = """Min lillebror och jag bodde i en liten, fredlig by. På en skinande grön kulle kunde man titta ut över hela samhället. Men vår startpunkt var inte enkel. Vi fick uppleva en hemsk tid. Det var en kontrast till ytan, där allt verkade bra.

Fram till år… ja, fram till år 1986, då en känd kärnkraftsolycka skedde, fanns det ingen oro. "Hur kommer det sig att…?" frågade min bror ofta när han hörde nyheterna. Ett populärt massmedium (böjning: massmediet, massmedier, massmedierna) rapporterade om farorna. Denna katastrof kunde leda till att många blev sjuka. En läkare i vår by blev tyvärr knivmördad och en annan kvinna hotades när någon försökte skjuta ihjäl henne i en bred backe. Det var helt sjukt! Gärningsmannen var en hjärtlös psykopat med ett sammasatt syndrom i sin hjärna. Han kände ingen sympati och kunde till och med ljuga och ta till en lögn i rätten.

Vi fick lära oss att alltid vara tillsammans för att trygga sin framtid. Det kunde finnas faror, och Socialstyrelsen varnade för att en ny infektionssjukdom var på väg. En sjuksköterska som var utbildad inom akutsjukvård sa: "Ställ frågor om du känner kramp i magen eller får en konstig pupill i ögat, och stanna hemma om du håller på att svimma." Medicinen hon gav kunde smaka illa, men den var noggrann, och man var väl omhändertagen. Man ville minska riskerna för att bli sämre. Att få vård i tid var viktigt.

Jag minns också att man kunde göra som man vill när det gällde preventivmedel. Men man var ibland osäker och trodde på felaktig information. Just det, vi var tvungna att skicka in en blankett för att få hjälp. Om någon hade ett handikapp och var funktionshindrad kunde en ambulans rulla in för att hämta dem. Många gånger var vi tvungna att hålla ett positivt kroppsspråk för att hjälpa dem att kalla på doktorer.

När jag nu brukar tänka tillbaka på de tio åren, vill jag tipsa alla om att värdesätta sin hälsa."""

core_words = [
    "kärnkraftsolycka", "skjuta ihjäl", "preventivmedel", "göra som man vill", 
    "infektionssjukdom", "Socialstyrelsen", "knivmördad", "trygga sin framtid", 
    "hjärtlös", "kulle", "tänka tillbaka", "fram till år…", "handikapp", 
    "funktionshindrad", "vara tillsammans", "utbildad inom", "massmedium", 
    "massmediet, massmedier, massmedierna)", "kramp", "by", "lillebror", 
    "svimma", "helt sjukt", "hjärna", "skinande", "leda till att", "kroppsspråk", 
    "pupill", "till ytan", "backe", "smaka illa", "psykopat", "ta till en lögn", 
    "syndrom", "omhändertagen", "få vård", "hålla"
]

glue_words = [
    "rulla", "tio", "ljuga", "osäker", "felaktig", "just det", "noggrann", 
    "kontrast", "sämre", "finnas", "ställ frågor", "startpunkt", "minska", 
    "titta ut över", "tipsa", "Hur kommer det sig att…?", "stanna", "sammasatt", 
    "kalla", "fredlig", "enkel", "bred", "skicka in"
]

target_mappings = [
    # Core
    ("kärnkraftsolycka", "kärnkraftsolycka"),
    ("skjuta ihjäl", "skjuta ihjäl"),
    ("preventivmedel", "preventivmedel"),
    ("göra som man vill", "göra som man vill"),
    ("infektionssjukdom", "infektionssjukdom"),
    ("Socialstyrelsen", "Socialstyrelsen"),
    ("knivmördad", "knivmördad"),
    ("trygga sin framtid", "trygga sin framtid"),
    ("hjärtlös", "hjärtlös"),
    ("kulle", "kulle"),
    ("tänka tillbaka", "tänka tillbaka"),
    ("fram till år…", "Fram till år…"),
    ("handikapp", "handikapp"),
    ("funktionshindrad", "funktionshindrad"),
    ("vara tillsammans", "vara tillsammans"),
    ("utbildad inom", "utbildad inom"),
    ("massmedium", "massmedium"),
    ("massmediet, massmedier, massmedierna)", "massmediet, massmedier, massmedierna)"),
    ("kramp", "kramp"),
    ("by", "by"),
    ("lillebror", "lillebror"),
    ("svimma", "svimma"),
    ("helt sjukt", "helt sjukt"),
    ("hjärna", "hjärna"),
    ("skinande", "skinande"),
    ("leda till att", "leda till att"),
    ("kroppsspråk", "kroppsspråk"),
    ("pupill", "pupill"),
    ("till ytan", "till ytan"),
    ("backe", "backe"),
    ("smaka illa", "smaka illa"),
    ("psykopat", "psykopat"),
    ("ta till en lögn", "ta till en lögn"),
    ("syndrom", "syndrom"),
    ("omhändertagen", "omhändertagen"),
    ("få vård", "få vård"),
    ("hålla", "hålla"),

    # Glue
    ("rulla", "rulla"),
    ("tio", "tio"),
    ("ljuga", "ljuga"),
    ("osäker", "osäker"),
    ("felaktig", "felaktig"),
    ("just det", "Just det"),
    ("noggrann", "noggrann"),
    ("kontrast", "kontrast"),
    ("sämre", "sämre"),
    ("finnas", "finnas"),
    ("ställ frågor", "Ställ frågor"),
    ("startpunkt", "startpunkt"),
    ("minska", "minska"),
    ("titta ut över", "titta ut över"),
    ("tipsa", "tipsa"),
    ("Hur kommer det sig att…?", "Hur kommer det sig att…?"),
    ("stanna", "stanna"),
    ("sammasatt", "sammasatt"),
    ("kalla", "kalla"),
    ("fredlig", "fredlig"),
    ("enkel", "enkel"),
    ("bred", "bred"),
    ("skicka in", "skicka in")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if " " in word_in_sentence or "." in word_in_sentence or "?" in word_in_sentence or "!" in word_in_sentence or "…" in word_in_sentence or "”" in word_in_sentence or "-" in word_in_sentence or "–" in word_in_sentence or "/" in word_in_sentence or ")" in word_in_sentence or "," in word_in_sentence:
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
    "step_id": "hälsa_medicin",
    "step_title": "Hälsa & Medicin",
    "article_id": "art_25",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('course/sfid/phase2/article_25.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
