import json
import re

text = """Varje morgon börjar vi en ny dag i en fantastisk värld full av tekniska lösningar. Det är otroligt att se hur mycket den moderna tekniken kan påverka vårt liv och vår vardag. För många år sedan var kroppsarbete mycket vanligt i samhället, och människor fick använda mycket energi från sin egen kropp för att överleva och sköta sitt jobb. I dag behöver vi egentligen inte arbeta lika hårt fysiskt, på grund av våra smarta maskiner och system som gör jobbet åt oss.

Nu för tiden är det i stället så att många sitter framför en dator hela dagen på kontoret. Min gode vän är civilingenjör och han har utvecklat en helt egen metod för att jobba mer effektivt. Han använder avancerad matematik och olika digitala redskap för att lösa komplexa problem i sitt projekt. Hans fru är geolog och hon undersöker naturen. Det är en rolig hobby, så de gillar både geologi och astronomi på fritiden.

Det skulle verkligen vara oerhört svårt att fungera i samhället utan elektricitet i dag. Om vi till exempel inte hade snabbt bredband, skulle vi tvingas vänta väldigt länge på all möjlig information från omvärlden. Jag gissar att mindre än hälften av oss vanligt folk faktiskt förstår all den komplicerade teknik vi använder. Man kan lätt göra fel när man ska välja ett bra verktyg för sitt arbete. Ibland känns det som att det finns för mycket information överallt. I går kväll satt jag och surfade, och jag hittade mycket information på nätet. Det var en spännande statistik som visade tydligt att vi i genomsnitt spenderar ungefär tre timmar varje kväll framför en teveskärm i vardagsrummet.

Många människor gillar verkligen att titta på teve på kvällen för att slappna av efter jobbet. En modern teve eller en smart teveapparat har numera väldigt många fantastiska funktioner, men man kan undra vilken man ska köpa för att få bäst bild. Vi har också en stor möjlighet att lära oss nya spännande saker via nätet, till exempel helt nya språk eller kulturer. Tidigt på morgonen läser jag ofta ett mejl från jobbet. Sedan, när jag går till bussen, kan jag snabbt skicka sms till min familj eller ringa ett viktigt telefonsamtal till en kollega.

Mitt i all denna teknik är det mycket viktigt att inte glömma sin kropp. Du kan med fördel delta i olika idrotter på helgerna, eftersom regelbunden fysisk aktivitet är avgörande för vår hälsa. Alla människor har naturligtvis inte samma styrka och alla orkar inte träna precis varje dag i veckan. Man måste helt enkelt hitta på rätt balans i livet för att må bra långsiktigt. Det kan förstås variera mycket hur man mår från dag till dag. Men genom att kunna använda tekniken på en hög nivå och samtidigt röra på sig, får vi mer tid över till varandra."""

core_words = [
    "teveskärm", "teve", "energi", "orka", "titta på teve", "hitta på", "dator",
    "jag hittade … på nätet", "mejl", "telefonsamtal", "skicka sms", "nätet",
    "civilingenjör", "teveapparat", "statistik", "geolog", "fysisk aktivitet",
    "kroppsarbete", "elektricitet", "bredband", "verktyg", "matematik", "astronomi"
]

glue_words = [
    "Varje", "börja", "ny", "fantastisk", "otrolig", "påverka", "få", "egentligen", 
    "hård", "på grund av", "hel", "egen", "redskap", "både", "skulle", "om", "vänta", 
    "gissa", "mindre än", "göra", "fel", "välja", "för mycket", "rolig", "ungefär", 
    "vilken", "möjlighet", "till exempel", "tidig", "glömma", "delta", "samma", 
    "rätt", "variera", "sin", "kunna", "hög"
]

target_mappings = [
    ("teveskärm", "teveskärm"),
    ("teve", "teve"),
    ("energi", "energi"),
    ("orka", "orkar"),
    ("titta på teve", "titta på teve"),
    ("hitta på", "hitta på"),
    ("dator", "dator"),
    ("jag hittade … på nätet", "jag hittade mycket information på nätet"),
    ("mejl", "mejl"),
    ("telefonsamtal", "telefonsamtal"),
    ("skicka sms", "skicka sms"),
    ("nätet", "nätet"),
    ("civilingenjör", "civilingenjör"),
    ("teveapparat", "teveapparat"),
    ("statistik", "statistik"),
    ("geolog", "geolog"),
    ("fysisk aktivitet", "fysisk aktivitet"),
    ("kroppsarbete", "kroppsarbete"),
    ("elektricitet", "elektricitet"),
    ("bredband", "bredband"),
    ("verktyg", "verktyg"),
    ("matematik", "matematik"),
    ("astronomi", "astronomi"),
    
    ("Varje", "Varje"),
    ("börja", "börjar"),
    ("ny", "ny"),
    ("fantastisk", "fantastisk"),
    ("otrolig", "otroligt"),
    ("påverka", "påverka"),
    ("få", "fick"),
    ("egentligen", "egentligen"),
    ("hård", "hårt"),
    ("på grund av", "på grund av"),
    ("hel", "hela"),
    ("egen", "egen"),
    ("redskap", "redskap"),
    ("både", "både"),
    ("skulle", "skulle"),
    ("om", "Om"),
    ("vänta", "vänta"),
    ("gissa", "gissar"),
    ("mindre än", "mindre än"),
    ("göra", "göra"),
    ("fel", "fel"),
    ("välja", "välja"),
    ("för mycket", "för mycket"),
    ("rolig", "rolig"),
    ("ungefär", "ungefär"),
    ("vilken", "vilken"),
    ("möjlighet", "möjlighet"),
    ("till exempel", "till exempel"),
    ("tidig", "Tidigt"),
    ("glömma", "glömma"),
    ("delta", "delta"),
    ("samma", "samma"),
    ("rätt", "rätt"),
    ("variera", "variera"),
    ("sin", "sin"),
    ("kunna", "kunna"),
    ("hög", "hög")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if base == "jag hittade … på nätet":
        start = text.find(word_in_sentence)
    else:
        escaped = re.escape(word_in_sentence)
        match = re.search(r'\b' + escaped + r'\b', text)
        if match:
            start = match.start()
        else:
            start = text.find(word_in_sentence)
            
    if start == -1:
        print(f"ERROR: could not find {word_in_sentence}")
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
    "step_id": "vetenskap_teknik",
    "step_title": "Vetenskap & Teknik",
    "article_id": "art_00",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('course/sfid/phase2/article_0.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
