import json
import re

text = """För många börjar ett arbetsliv när de ska söka jobb för första gången. "Vad ville hon bli?" frågade min chef. Min vän var från en vanlig arbetarfamilj utanför staden, vars föräldrar var arbetare. Hon ville inte bli präst, utan ville jobba på en fabrik. Hon började som sommarjobbare. Det var möjligt att de skulle anställa henne permanent direkt efter sommaren. "Hur många år har hon jobbat här?" frågade jag. Hon var nyss anställd.

Fabriken var ett stort livmedelsföretag. De hade ett gott samarbete med ett stort tevebolag. Det fanns ingen annan arbetsgivare som kunde konkurrera med deras resultat. Företaget var kanske en tredjedel så stort som de största i världen, men de var ändå framgångsrika. De planerade att ingå partnerskap med en utländsk partner, trots att de behövde en bra taktik. För att prestera högst upp, var de tvungna att sätta upp ett tydligt mål.

Men det var inte…förrän en ny chef tog över som problem började drabba dem. Vissa regler saknade logisk mening. De hade post som alltid kom sent och de glömde beställa kontormaterial. Det var viktigt att fack och personal fick bra arbetsvillkor och lika lön för lika arbete. Annars kunde de avskeda folk. En chef sa: "I have a dream." Han talade om passfrihet och att man skulle referera till franska metoder.

"Det passar bra." sa en kollega. "Vi måste rapportera allt vi gör. Vi ska skapa nya regler under min mandatperiod och skicka ut dem." Han tog mycket ansvar för sin nya roll. Han sa också till de anställda: "Vänligen följ varje instruktion noga." Han bad oss vara mer kreativ och att vi måste lämna tillbaka allt vi lånar.

Jag skrev ett mejl till honom: "Jag vore tacksam om … ni kunde ge mig mer tid. Skulle ni kunna skicka…? mer information efter mötet? Med vänliga hälsningar, en som försöker vara ett proffs längst bak i rummet." """

core_words = [
    "anställa", "sommarjobbare", "samarbete", "mandatperiod", "post", "tevebolag", 
    "Hur många år har du/han/hon jobbat här?", "have", "lika lön för lika arbete", "fabrik", 
    "arbetarfamilj", "arbetare", "arbetsgivare", "fack", "arbetsvillkor", "avskeda", 
    "livmedelsföretag", "ingå partnerskap", "arbetsliv", "drabba", "passfrihet", "Det passar bra.", 
    "söka jobb", "anställd", "kontormaterial", "proffs", "ansvar", "vänliga hälsningar", 
    "roll", "resultat", "mål", "planera", "Jag vore tacksam om …", "vänligen", "instruktion", 
    "skapa", "skicka", "Skulle ni kunna skicka…?", "taktik", "prestera", "präst"
]

glue_words = [
    "möjlig", "konkurrera", "referera", "efter", "kreativ", "vars", "ingen", "franska", 
    "rapportera", "längst", "en tredjedel så stort som", "logisk", "lämna tillbaka", 
    "direkt efter", "inte…förrän", "Vad ville hon bli?", "högst", "utanför", "trots att"
]

target_mappings = [
    ("anställa", "anställa"),
    ("sommarjobbare", "sommarjobbare"),
    ("samarbete", "samarbete"),
    ("mandatperiod", "mandatperiod"),
    ("post", "post"),
    ("tevebolag", "tevebolag"),
    ("Hur många år har du/han/hon jobbat här?", "Hur många år har hon jobbat här?"),
    ("have", "have"),
    ("lika lön för lika arbete", "lika lön för lika arbete"),
    ("fabrik", "fabrik"),
    ("arbetarfamilj", "arbetarfamilj"),
    ("arbetare", "arbetare"),
    ("arbetsgivare", "arbetsgivare"),
    ("fack", "fack"),
    ("arbetsvillkor", "arbetsvillkor"),
    ("avskeda", "avskeda"),
    ("livmedelsföretag", "livmedelsföretag"),
    ("ingå partnerskap", "ingå partnerskap"),
    ("arbetsliv", "arbetsliv"),
    ("drabba", "drabba"),
    ("passfrihet", "passfrihet"),
    ("Det passar bra.", "Det passar bra."),
    ("söka jobb", "söka jobb"),
    ("anställd", "anställd"),
    ("kontormaterial", "kontormaterial"),
    ("proffs", "proffs"),
    ("ansvar", "ansvar"),
    ("vänliga hälsningar", "vänliga hälsningar"),
    ("roll", "roll"),
    ("resultat", "resultat"),
    ("mål", "mål"),
    ("planera", "planerade"),
    ("Jag vore tacksam om …", "Jag vore tacksam om …"),
    ("vänligen", "Vänligen"),
    ("instruktion", "instruktion"),
    ("skapa", "skapa"),
    ("skicka", "skicka"),
    ("Skulle ni kunna skicka…?", "Skulle ni kunna skicka…?"),
    ("taktik", "taktik"),
    ("prestera", "prestera"),
    ("präst", "präst"),
    
    # Glue
    ("möjlig", "möjligt"),
    ("konkurrera", "konkurrera"),
    ("referera", "referera"),
    ("efter", "efter"),
    ("kreativ", "kreativ"),
    ("vars", "vars"),
    ("ingen", "ingen"),
    ("franska", "franska"),
    ("rapportera", "rapportera"),
    ("längst", "längst"),
    ("en tredjedel så stort som", "en tredjedel så stort som"),
    ("logisk", "logisk"),
    ("lämna tillbaka", "lämna tillbaka"),
    ("direkt efter", "direkt efter"),
    ("inte…förrän", "inte…förrän"),
    ("Vad ville hon bli?", "Vad ville hon bli?"),
    ("högst", "högst"),
    ("utanför", "utanför"),
    ("trots att", "trots att")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if base == "efter":
        start = text.find("efter mötet")
    elif base == "skicka":
        start = text.find("skicka ut dem")
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
    "step_id": "arbetsliv",
    "step_title": "Arbetsliv",
    "article_id": "art_06",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('course/sfid/phase2/article_6.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
