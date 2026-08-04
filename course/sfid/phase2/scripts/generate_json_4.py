import json
import re

text = """Min vän, som ursprungligen är från en liten by norrut, gillar att resa. Hon ville komma ifrån sin vanliga stad, eftersom hon kände en stor förändring närma sig med stora steg. Hon hade varit bortrest flera gånger och nu var det dags för en ny lång vistelse. Som nyinflyttad i en ny stad kände hon sig ofta ensam, så resor gav henne stöd.

"Jag vill uppleva en milsvid utsikt och besöka en gammal fästning," började hon säga. "Nähä! Vill du verkligen det?" frågade jag. Hon nickade. Först skulle hon ta ett flyg, landa med en mellanlandning och sedan ta en passagerarfärja. Efter hennes ankomst skulle hon hyra ett fordon för att åka många mil till kusten. "Close your eyes," sa hon på engelska när vi lyssnade på en lokal radiosändning om resor.

När hon äntligen var framme vid vattnet, bestämde hon sig för att hyra en kajak. "Man måste ha bra balans i en kajak för att inte drunkna," sa en trevlig hotellägare. Det fanns alla sorters båtar där, till och med en gammal långbåt och ett stort skepp. Hon lät kajaken glida fram över vattnet. Hon valde att bara flyta med strömmen och gradvis slappna av. Hon kunde se barn springa runt på stranden och en hund springa lös.

På kvällen åt hon katrinplommon och tänkte på sitt uppbrott från sitt gamla liv. En äldre man, klädd som en kardinal, berättade om män som brukade rista namn i stenar och grunda nya städer i hela världen. "Sök i dig själv," sa han. Allt verkade flyta på väldigt bra och det kändes aldrig som en katastrof. Hon ville inte ha en halv semester, utan en helt underbar tid. En ovanlig resenär vill alltid gå lite längre bort. På det sättet blir det aldrig tråkigt i längden. Jag hoppas att hon vill komma tillbaka och göra ett återbesök hos mig. Det vore synd att byta ut en viss del av livet när det inte är en dålig sak, men jag förstod att hon var lycklig när hon gick ner till havet."""

core_words = [
    "komma ifrån", "ursprungligen", "katrinplommon", "radiosändning", "närma sig med stora steg", 
    "längre bort", "passagerarfärja", "drunkna", "kardinal", "grunda", "rista", "skepp", "långbåt", 
    "uppbrott", "stöd", "Nähä!", "springa runt", "återbesök", "bortrest", "springa lös", "nyinflyttad", 
    "flyta på", "i längden", "eyes,", "resenär", "flyta med", "vistelse", "hotellägare", "fordon", 
    "på det sättet", "mil", "kajak", "norrut", "milsvid", "fästning", "glida fram", "mellanlandning", 
    "landa", "ankomst"
]

glue_words = [
    "säga", "komma", "hela", "byta", "stor", "först", "ner", "dålig", "när", "flera", 
    "alla", "man", "lång", "sak", "balans", "gradvis", "halv", "viss", "ovanlig", "sök", 
    "katastrof"
]

target_mappings = [
    # Core
    ("komma ifrån", "komma ifrån"),
    ("ursprungligen", "ursprungligen"),
    ("katrinplommon", "katrinplommon"),
    ("radiosändning", "radiosändning"),
    ("närma sig med stora steg", "närma sig med stora steg"),
    ("längre bort", "längre bort"),
    ("passagerarfärja", "passagerarfärja"),
    ("drunkna", "drunkna"),
    ("kardinal", "kardinal"),
    ("grunda", "grunda"),
    ("rista", "rista"),
    ("skepp", "skepp"),
    ("långbåt", "långbåt"),
    ("uppbrott", "uppbrott"),
    ("stöd", "stöd"),
    ("Nähä!", "Nähä!"),
    ("springa runt", "springa runt"),
    ("återbesök", "återbesök"),
    ("bortrest", "bortrest"),
    ("springa lös", "springa lös"),
    ("nyinflyttad", "nyinflyttad"),
    ("flyta på", "flyta på"),
    ("i längden", "i längden"),
    ("eyes,", "eyes,"),
    ("resenär", "resenär"),
    ("flyta med", "flyta med"),
    ("vistelse", "vistelse"),
    ("hotellägare", "hotellägare"),
    ("fordon", "fordon"),
    ("på det sättet", "På det sättet"),
    ("mil", "mil"),
    ("kajak", "kajak"),
    ("norrut", "norrut"),
    ("milsvid", "milsvid"),
    ("fästning", "fästning"),
    ("glida fram", "glida fram"),
    ("mellanlandning", "mellanlandning"),
    ("landa", "landa"),
    ("ankomst", "ankomst"),

    # Glue
    ("säga", "säga"),
    ("komma", "komma"),
    ("hela", "hela"),
    ("byta", "byta"),
    ("stor", "stor"),
    ("först", "Först"),
    ("ner", "ner"),
    ("dålig", "dålig"),
    ("när", "när"),
    ("flera", "flera"),
    ("alla", "alla"),
    ("man", "Man"),
    ("lång", "lång"),
    ("sak", "sak"),
    ("balans", "balans"),
    ("gradvis", "gradvis"),
    ("halv", "halv"),
    ("viss", "viss"),
    ("ovanlig", "ovanlig"),
    ("sök", "Sök"),
    ("katastrof", "katastrof")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if base == "komma":
        start = text.find("komma tillbaka")
    elif base == "när":
        start = text.find("när vi lyssnade")
    else:
        if " " in word_in_sentence or "." in word_in_sentence or "!" in word_in_sentence or "," in word_in_sentence:
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
    "step_id": "resor_transport",
    "step_title": "Resor & Transport",
    "article_id": "art_04",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('./course/sfid/phase2/article_4.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
