import json
import re

text = """En nödvändig paus från staden är viktig när man jobbar mycket. Därför bestämde jag mig för att hyra en rustik stuga vid en gammal bondgård över en helg. Jag ville logga ut och inte stressa.

Innan jag åkte fick jag en inbjudan till en rolig utekväll med ett par vänner. Men jag tackade nej. En gäst i mitt hus i staden var en snäll gammal änka som gillade att sätta guldkant på tillvaron. Vi brukade ha en guldkant på lördagskvällen med en lyxig pralinask. Det kunde säkert ersätta utekvällen ett tag, men nu behövde jag vila. 

I stugan, ovanför en mörk källare, fanns det en liten lucka i golvet. Jag ville inte alls öppna den, och inte heller gå ner dit. Har du hört talas om historien om råttan i pizzan? Urban legends brukar fascinera mig, och källaren kändes som en läskig plats. Istället stannade jag uppe och läste en dagstidning en lång stund. 

För riktig avkoppling hade stugan en gammal färgteve och en mikro, men ingen annan modern pryl. På gården träffade jag en kund till bonden, en kvinna med en fin frisyr och en stor hatt. Vi hade faktiskt samma efternamn. Vi stod vid en kant av åkern och pratade. Jag märkte att hon hade en ovana att bita på naglarna. Hon hade ett fult tuggmärke på sitt finger. Hon brukade också smaska när hon åt och ibland svära. Vissa människor brukar även peta sig i näsan, vilket är en annan tråkig grej. 

I jämförelse med staden fanns det ingen gräns för naturen. Jag hittade en tung yxa för att hugga ved. Man kunde spendera ytterligare många timmar på detta arbete. Att vara myndig betyder att man får bestämma själv, men jag ville bara vara här och göra fin middag för en krona, om man nu hade råd att laga mat billigt. Kanske fanns det ett gemensamt dam- och herrbad i byn som man kunde besöka? Men stugan var helt klart bäst. Innan vi skulle stänga för kvällen fick jag spola ner en liten spindel i toaletten. Sedan somnade jag gott."""

core_words = [
    "lucka", "källare", "hatt", "smaska", "bita på naglarna", "utekväll", 
    "tuggmärke", "pralinask", "kund", "peta sig i näsan", "pryl", "krona", 
    "svära", "ovana", "gäst", "guldkant", "inbjudan", "yxa", "avkoppling", 
    "rustik", "kant", "dam- och herrbad", "frisyr", "hyra", "bondgård", 
    "stuga", "färgteve", "efternamn", "mikro", "myndig", "stressa", 
    "logga ut", "sätta guldkant på", "dagstidning"
]

glue_words = [
    "nödvändig", "ett tag", "råttan i pizzan", "spola ner", "ersätta", 
    "helg", "gräns", "göra fin", "ytterligare", "säkert", "inte alls", 
    "helt klart", "stänga", "inte heller", "vid", "fascinera", "jämförelse", 
    "en lång stund", "hört talas om", "dit", "råd", "ovanför", "därför", 
    "spendera", "par", "änka"
]

target_mappings = [
    # Core
    ("lucka", "lucka"),
    ("källare", "källare"),
    ("hatt", "hatt"),
    ("smaska", "smaska"),
    ("bita på naglarna", "bita på naglarna"),
    ("utekväll", "utekväll"),
    ("tuggmärke", "tuggmärke"),
    ("pralinask", "pralinask"),
    ("kund", "kund"),
    ("peta sig i näsan", "peta sig i näsan"),
    ("pryl", "pryl"),
    ("krona", "krona"),
    ("svära", "svära"),
    ("ovana", "ovana"),
    ("gäst", "gäst"),
    ("guldkant", "guldkant"),
    ("inbjudan", "inbjudan"),
    ("yxa", "yxa"),
    ("avkoppling", "avkoppling"),
    ("rustik", "rustik"),
    ("kant", "kant"),
    ("dam- och herrbad", "dam- och herrbad"),
    ("frisyr", "frisyr"),
    ("hyra", "hyra"),
    ("bondgård", "bondgård"),
    ("stuga", "stuga"),
    ("färgteve", "färgteve"),
    ("efternamn", "efternamn"),
    ("mikro", "mikro"),
    ("myndig", "myndig"),
    ("stressa", "stressa"),
    ("logga ut", "logga ut"),
    ("sätta guldkant på", "sätta guldkant på"),
    ("dagstidning", "dagstidning"),

    # Glue
    ("nödvändig", "nödvändig"),
    ("ett tag", "ett tag"),
    ("råttan i pizzan", "råttan i pizzan"),
    ("spola ner", "spola ner"),
    ("ersätta", "ersätta"),
    ("helg", "helg"),
    ("gräns", "gräns"),
    ("göra fin", "göra fin"),
    ("ytterligare", "ytterligare"),
    ("säkert", "säkert"),
    ("inte alls", "inte alls"),
    ("helt klart", "helt klart"),
    ("stänga", "stänga"),
    ("inte heller", "inte heller"),
    ("vid", "vid"),
    ("fascinera", "fascinera"),
    ("jämförelse", "jämförelse"),
    ("en lång stund", "en lång stund"),
    ("hört talas om", "hört talas om"),
    ("dit", "dit"),
    ("råd", "råd"),
    ("ovanför", "ovanför"),
    ("därför", "Därför"),
    ("spendera", "spendera"),
    ("par", "par"),
    ("änka", "änka")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if base == "vid":
        start = text.find(" vid ") + 1
    elif base == "par":
        start = text.find("ett par vänner") + 4
    elif base == "råd":
        start = text.find("hade råd") + 5
    elif base == "guldkant":
        start = text.find("en guldkant") + 3
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
    "article_id": "art_34",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('course/sfid/phase2/article_34.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
