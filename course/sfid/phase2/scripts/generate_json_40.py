import json
import re

text = """"Vad för sorts… person är du egentligen?" frågade min vän, som är en känd arkitekt. Han är också en mycket modeintresserad man, precis som sin syster. 
"Det spelar ingen roll." svarade jag lugnt och hällde upp lite vatten i ett vackert glas. "Jag är bara en glad människa som gillar att ha skoj och roa sig varje dag."

Vårt lilla gäng var ett ganska brokigt sällskap. Vi bestod av en känd författare, en smart filosof, en smidig akrobat och en fantastisk musiker med extremt stor musikalisk talang, som ofta spelade saxofon och var en duktig trubadur. En av oss brukade samla på en unik vinylskiva från varje nytt decennium. Vi kom från Sverige och från andra länder, ungefär som en självstyrande liten familj. Vi brukade ofta campa, men vår gamla bil var alltid överbelastad. Ibland kändes det som ett helvete att packa. Vårt stora tält låg längst ner under all packning, men vi ville se världen innan dagarna blev ljusare och varmare.

Ibland gick vi på ett stort lajv utomhus där vi fick tävla om en glänsande guldnyckel. En av deltagarna var en rolig kille som såg ut som en naken sumobrottare. Han hade mycket naturlig komik i sig. Han var nästan som en populär komiker och skapade ofta en komisk stämning. Jag skrev om det i min dagbok. Det var nästan som en spännande saga. 

Vi älskade också naturen. Vi brukade cykla i skogen på sommaren, eller åka skidor på vintern. Min vän ville spela golf och letade ständigt efter sin bästa golfklubba. En dag såg vi en tyst jägare som skulle ut och jaga i skogen för att döda vilda djur. Ett litet djur hade en bruten vinge. "Akta dig för huggormsbett framför stugan," varnade jägaren och pekade på en specifik punkt i gräset.

Trots farorna tänkte vi stanna. "Vi ska fira jul i den här skogen," sa jag glatt. 
Min kompis var en extremt kuturintresserad person. Han gillade vacker konst med naturinspirerade motiv för att komplettera sin samling. I sin väska hade han en liten burk med god färg och ville måla. Han brukade säga ett gammalt ordspråk: "Man ska aldrig bränna sina broar." Han ville också gärna titta på den gamla svenska filmen ”Sommaren med Monica” med sin stora idol. Han tyckte att varje vacker rörelse i filmen var djupt romantisk. En annan person i gruppen ville bara skrapa på en liten trisslott eller hoppa från ett högt hopptorn vid sjön. Det fanns alltid något trevligt att göra, vare sig man ville simma eller bara cykla runt på vägarna."""

core_words = [
    "musiker", "musikalisk", "modeintresserad", "arkitekt", "samla", 
    "motiv", "författare", "naken", "filosof", "tält", "glas", "idol", 
    "akrobat", "lajv", "ordspråk", "kuturintresserad", "tävla", "dagbok", 
    "guldnyckel", "skrapa", "fira jul", "hopptorn", "cykla", "jägare", 
    "ha skoj", "komisk", "komik", "sumobrottare", "jaga", "komiker", 
    "golfklubba", "saga", "saxofon", "roa sig", "romantisk", "cykla", 
    "”Sommaren med Monica”", "åka skidor", "trubadur"
]

glue_words = [
    "Det spelar ingen roll.", "framför", "huggormsbett", "komplettera", 
    "andra länder", "längst ner", "decennium", "precis som", "ljusare", 
    "vinge", "bränna", "döda", "Vad för sorts…", "rörelse", "god", 
    "vinylskiva", "helvete", "burk", "självstyrande", "punkt", "överbelastad"
]

target_mappings = [
    # Core
    ("musiker", "musiker"),
    ("musikalisk", "musikalisk"),
    ("modeintresserad", "modeintresserad"),
    ("arkitekt", "arkitekt"),
    ("samla", "samla"),
    ("motiv", "motiv"),
    ("författare", "författare"),
    ("naken", "naken"),
    ("filosof", "filosof"),
    ("tält", "tält"),
    ("glas", "glas"),
    ("idol", "idol"),
    ("akrobat", "akrobat"),
    ("lajv", "lajv"),
    ("ordspråk", "ordspråk"),
    ("kuturintresserad", "kuturintresserad"),
    ("tävla", "tävla"),
    ("dagbok", "dagbok"),
    ("guldnyckel", "guldnyckel"),
    ("skrapa", "skrapa"),
    ("fira jul", "fira jul"),
    ("hopptorn", "hopptorn"),
    ("cykla", "cykla"),
    ("jägare", "jägare"),
    ("ha skoj", "ha skoj"),
    ("komisk", "komisk"),
    ("komik", "komik"),
    ("sumobrottare", "sumobrottare"),
    ("jaga", "jaga"),
    ("komiker", "komiker"),
    ("golfklubba", "golfklubba"),
    ("saga", "saga"),
    ("saxofon", "saxofon"),
    ("roa sig", "roa sig"),
    ("romantisk", "romantisk"),
    ("cykla", "cykla"),
    ("”Sommaren med Monica”", "”Sommaren med Monica”"),
    ("åka skidor", "åka skidor"),
    ("trubadur", "trubadur"),

    # Glue
    ("Det spelar ingen roll.", "Det spelar ingen roll."),
    ("framför", "framför"),
    ("huggormsbett", "huggormsbett"),
    ("komplettera", "komplettera"),
    ("andra länder", "andra länder"),
    ("längst ner", "längst ner"),
    ("decennium", "decennium"),
    ("precis som", "precis som"),
    ("ljusare", "ljusare"),
    ("vinge", "vinge"),
    ("bränna", "bränna"),
    ("döda", "döda"),
    ("Vad för sorts…", "Vad för sorts…"),
    ("rörelse", "rörelse"),
    ("god", "god"),
    ("vinylskiva", "vinylskiva"),
    ("helvete", "helvete"),
    ("burk", "burk"),
    ("självstyrande", "självstyrande"),
    ("punkt", "punkt"),
    ("överbelastad", "överbelastad")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if word_in_sentence == "cykla" and "cykla" in [w["word_in_sentence"] for w in words_json]:
        start = text.rfind("cykla")
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
    "article_id": "art_40",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('course/sfid/phase2/article_40.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
