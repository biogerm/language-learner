import json
import re

text = """När man reser norrut i landet, kan man besöka en känd kulturattraktion som har överlevt mer än ett årtionde. Kultur är viktigt för många, och när det gäller nöje är denna plats mer eller mindre fantastisk. 

Det gamla huset var en gång i tiden knutet till ett lokalt jordbruk, men nu vill man bidra till att vi får uppleva mycket roligt. Vissa personer är absolut en nolla på att sjunga och dansa, men här kan man ändå vara med i en stor kör. Ibland spelas vacker musik och folk bjuds in till en traditionell dans eller till och med en spännande maskeradbal. En känd kulturpersonlighet brukar ofta söka kontakt med unga artister här.

Andra gillar konst. I en stor sal finns en imponerande konstsamling. Du kan få en utställningskatalog för att lära dig mer om varje utställning. En berömd dansk konstnär har sin bästa målning här. Att måla en vacker tavla eller att bara rita med blyerts är en tyst och skön upplevelse. Ibland kan man också titta på ett fint foto eller ett gammalt historiskt dokument. "Man kan verkligen undra vem som gjorde denna?", brukar besökare säga.

Men det finns en annan del också. Kanske vill du vara med? Vissa går till en schackklubb för att spela schack tillsammans. Det spelas även brädspel och folk brukar spela kort på fredagskvällarna. Andra gillar att spela dataspel hela natten. En del vill hellre spela teater och drömmer om att bli en bra skådelspelare en dag. Även om det finns en syn på konst som något strikt, är det viktigt att veta att alla intressen får ta plats. Kulturen ska inte dö ut. 

Kanske gillar du sport? På husets egen sportbar kan man se en viktig match på tv. En person äter en god proteinkaka medan den andra har druckit mycket och nästan brutit sin pinne mitt itu. Man behöver inte ha någon bra bollkänsla för att heja, och man behöver inte ens en boll för att ha kul. Ibland visas även kampsport, och det verkar inte spela roll vad du gillar. Det finns en kulturell mix för alla, och allt detta är en liten utgift för mycket glädje. Det är alltså en klubb och plats där poesi möter vild fest. 

Jag gick därifrån med ett leende, full av inspiration och en konditional kärlek till kultur."""

core_words = [
    "sportbar", "vara med i", "kultur", "kulturattraktion", "proteinkaka", 
    "sjunga", "musik", "match", "dans", "kampsport", "bollkänsla", "boll", 
    "vara med", "spela teater", "kör", "poesi", "kulturell", "en del", 
    "jordbruk", "utställning", "utställningskatalog", "klubb", "spela schack", 
    "schackklubb", "spela dataspel", "spela roll", "kulturpersonlighet", 
    "konstnär", "fest", "konstsamling", "rita", "spela kort", "tavla", 
    "måla", "målning", "maskeradbal", "skådelspelare", "dansa", "foto"
]

glue_words = [
    "norrut", "när det gäller", "mer eller mindre", "dansk", "bidra till", 
    "söka kontakt", "undra", "mitt itu", "årtionde", "syn", "nolla", "tyst", 
    "dokument", "dö ut", "utgift", "den andra", "absolut", "därifrån", 
    "verkligen", "konditional", "alltså"
]

target_mappings = [
    # Core
    ("sportbar", "sportbar"),
    ("vara med i", "vara med i"),
    ("kultur", "Kultur"),
    ("kulturattraktion", "kulturattraktion"),
    ("proteinkaka", "proteinkaka"),
    ("sjunga", "sjunga"),
    ("musik", "musik"),
    ("match", "match"),
    ("dans", "dans"),
    ("kampsport", "kampsport"),
    ("bollkänsla", "bollkänsla"),
    ("boll", "boll"),
    ("vara med", "vara med"),
    ("spela teater", "spela teater"),
    ("kör", "kör"),
    ("poesi", "poesi"),
    ("kulturell", "kulturell"),
    ("en del", "En del"),
    ("jordbruk", "jordbruk"),
    ("utställning", "utställning"),
    ("utställningskatalog", "utställningskatalog"),
    ("klubb", "klubb"),
    ("spela schack", "spela schack"),
    ("schackklubb", "schackklubb"),
    ("spela dataspel", "spela dataspel"),
    ("spela roll", "spela roll"),
    ("kulturpersonlighet", "kulturpersonlighet"),
    ("konstnär", "konstnär"),
    ("fest", "fest"),
    ("konstsamling", "konstsamling"),
    ("rita", "rita"),
    ("spela kort", "spela kort"),
    ("tavla", "tavla"),
    ("måla", "måla"),
    ("målning", "målning"),
    ("maskeradbal", "maskeradbal"),
    ("skådelspelare", "skådelspelare"),
    ("dansa", "dansa"),
    ("foto", "foto"),

    # Glue
    ("norrut", "norrut"),
    ("när det gäller", "när det gäller"),
    ("mer eller mindre", "mer eller mindre"),
    ("dansk", "dansk"),
    ("bidra till", "bidra till"),
    ("söka kontakt", "söka kontakt"),
    ("undra", "undra"),
    ("mitt itu", "mitt itu"),
    ("årtionde", "årtionde"),
    ("syn", "syn"),
    ("nolla", "nolla"),
    ("tyst", "tyst"),
    ("dokument", "dokument"),
    ("dö ut", "dö ut"),
    ("utgift", "utgift"),
    ("den andra", "den andra"),
    ("absolut", "absolut"),
    ("därifrån", "därifrån"),
    ("verkligen", "verkligen"),
    ("konditional", "konditional"),
    ("alltså", "alltså")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if base == "vara med":
        start = text.find("vill du vara med?") + 8
    elif base == "vara med i":
        start = text.find("vara med i en stor kör")
    elif base == "kultur":
        start = text.find("Kultur är")
    elif base == "en del":
        start = text.find("En del vill hellre")
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
    "step_id": "kultur_nöje",
    "step_title": "Kultur & Nöje",
    "article_id": "art_35",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('./course/sfid/phase2/article_35.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
