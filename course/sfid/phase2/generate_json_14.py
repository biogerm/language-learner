import json
import re

text = """I Sverige kan en måltid ha ett speciellt tema. Först och främst har vi fika. Att fika kan vara så enkelt som att dricka ett glas saft och äta en macka på ett litet fik. Vissa föredrar kall mjölk, medan andra tar ett glas vin till en sen middag. "Det är fint?" frågade en vän från utlandet när hon såg min hemlagade mat.

En typisk svensk vardagsmat är kokt potatis och en köttbulle. Man kan ha i lite krydda, till exempel kryddpeppar. "Men ni äter väl inte hästkött?" undrade hon. "Jo, det är sant!" sa jag. Förr fanns inget förbud mot det, även om man var tvungen att äta vad som fanns, särskilt under en historisk oljekris. Men hon slapp vara rädd för det nu. Hon ville inte ge kritik, men tyckte idén var lite knäppt.

Jag lagade också palt, en gammal rätt bakad på vetemjöl och potatis. Den serveras med mycket smör och lingonsylt. "Å ena sidan… å andra sidan," började min vän, "är det jättegott, men man får ju paltkoma." För att hon inte skulle bli slagen av trötthet, så bestämde vi oss för att gå ut. Vi tog ett dopp. Efter flera salta bad fick vi ny energi.

Vi firade den varma månaden juni genom att äta mer. Solens låga fallvinkel över havet var vacker. Vi tittade på en gammal film, en riktig snyftare, medan vi åt dessert. Jag hade gjort en ugnsgräddad pannkaka med en klick äggost. Vi hade också en äppelkaka kryddad med kanel och prydd med minst en äppelklyfta. Dessutom fanns färsk jordgubbe och några björnbär som verkade vara begravd under grädden.

"Denna rätt bör höra till en officiell meny," sa hon. "Tack, men nästa gång kanske jag lagar kryddig thaimat med paprika och lite riven parmesan på toppen, även om det kräver en lång förklaring av ett svårt recept steg för steg," skrattade jag."""

core_words = [
    "mjölk", "saft", "jordgubbe", "vin", "macka", "fik", "salta bad", "snyftare", 
    "palt", "kokt", "potatis", "vetemjöl", "smör", "lingonsylt", "paltkoma", 
    "bakad på", "ugnsgräddad", "pannkaka", "björnbär", "krydda", "fika", "thaimat", 
    "äggost", "hemlagad", "vardagsmat", "hästkött", "köttbulle", "middag", "måltid", 
    "äppelkaka", "kryddad med", "kryddpeppar", "äppelklyfta", "paprika", "parmesan", 
    "recept", "oljekris", "bli slagen"
]

glue_words = [
    "höra till", "knäppt", "Det är fint?", "Jo, det är sant!", "tema", "steg", "låg", 
    "bör", "kritik", "juni", "fallvinkel", "gå ut", "först och främst", "förklaring", 
    "bestämma", "förbud", "tvungen att", "begravd", "minst", "officiell", 
    "vara rädd för", "å ena sidan… å andra sidan"
]

target_mappings = [
    # Core
    ("mjölk", "mjölk"),
    ("saft", "saft"),
    ("jordgubbe", "jordgubbe"),
    ("vin", "vin"),
    ("macka", "macka"),
    ("fik", "fik"),
    ("salta bad", "salta bad"),
    ("snyftare", "snyftare"),
    ("palt", "palt"),
    ("kokt", "kokt"),
    ("potatis", "potatis"),
    ("vetemjöl", "vetemjöl"),
    ("smör", "smör"),
    ("lingonsylt", "lingonsylt"),
    ("paltkoma", "paltkoma"),
    ("bakad på", "bakad på"),
    ("ugnsgräddad", "ugnsgräddad"),
    ("pannkaka", "pannkaka"),
    ("björnbär", "björnbär"),
    ("krydda", "krydda"),
    ("fika", "fika"),
    ("thaimat", "thaimat"),
    ("äggost", "äggost"),
    ("hemlagad", "hemlagade"),
    ("vardagsmat", "vardagsmat"),
    ("hästkött", "hästkött"),
    ("köttbulle", "köttbulle"),
    ("middag", "middag"),
    ("måltid", "måltid"),
    ("äppelkaka", "äppelkaka"),
    ("kryddad med", "kryddad med"),
    ("kryddpeppar", "kryddpeppar"),
    ("äppelklyfta", "äppelklyfta"),
    ("paprika", "paprika"),
    ("parmesan", "parmesan"),
    ("recept", "recept"),
    ("oljekris", "oljekris"),
    ("bli slagen", "bli slagen"),

    # Glue
    ("höra till", "höra till"),
    ("knäppt", "knäppt"),
    ("Det är fint?", "Det är fint?"),
    ("Jo, det är sant!", "Jo, det är sant!"),
    ("tema", "tema"),
    ("steg", "steg"),
    ("låg", "låga"),
    ("bör", "bör"),
    ("kritik", "kritik"),
    ("juni", "juni"),
    ("fallvinkel", "fallvinkel"),
    ("gå ut", "gå ut"),
    ("först och främst", "Först och främst"),
    ("förklaring", "förklaring"),
    ("bestämma", "bestämde"),
    ("förbud", "förbud"),
    ("tvungen att", "tvungen att"),
    ("begravd", "begravd"),
    ("minst", "minst"),
    ("officiell", "officiell"),
    ("vara rädd för", "vara rädd för"),
    ("å ena sidan… å andra sidan", "Å ena sidan… å andra sidan")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if base == "potatis":
        start = text.find("kokt potatis") + 5
    elif base == "krydda":
        start = text.find("lite krydda") + 5
    elif base == "fika":
        start = text.find("har vi fika.") + 7
    elif base == "steg":
        start = text.find("recept steg för") + 7
    elif " " in word_in_sentence or "." in word_in_sentence or "?" in word_in_sentence or "!" in word_in_sentence or "…" in word_in_sentence:
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
    "step_id": "mat_matlagning",
    "step_title": "Mat & Matlagning",
    "article_id": "art_14",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('./course/sfid/phase2/article_14.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
