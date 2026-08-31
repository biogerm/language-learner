import json
import re

text = """Jag och min kurskompis bestämde oss för att gå till ett bibliotek för att repetera inför ett stort prov. "Har du lust att…?" frågade hon, och ville föreslå att vi skulle studera på en klämdag. "Vad säger du?" Jag tyckte det lät bra, så vi kunde få så många som möjligt timmar att läsa.

Vi valde att diskutera svensk grammatik. Vår uppgift skulle bestå av en skriftlig del och en muntlig redovisning. En fördel var att vi hade en lång ordlista att öva på. Vi fick en lapp där varje ruta innehöll ett påstående. Varje mening hade ett viktigt begrepp. Vi fick i uppdrag att stryka under varje nyckelord och sedan sammanfatta allt.

Vi började med en ordkunkskapsövning. Vi tränade ordkunskap genom att titta på en vokal, en konsonant och varje stavelse. Det var roligt. "Du är skicklig," poängterade hon. Vi pratade också om ljudförändringar, som svag reduktion och asssimilation. Vi ville bevisa vad vi hade lärt oss. 

Sedan gick vi igenom olika ordklasser och satsdelar. Vi lärde oss att hitta ett subjekt. Vi jämförde bestämd form med obestämd form, och tränade på adjektivets komparativ. Vi tittade på reflexiv pronomen, och lärde oss när man använder supinum och imperativ. Vi försökte också att betona rätt.

Vi tränade på att bygga meningar. En mening kan börja med en huvudsats och följas av en bisats. Vi såg hur en konjunktion, en subjunktion eller en prepostion kan förändra allt. Vi lärde oss att skriva direkt tal. En nackdel med grammatik är att det finns så många regler att komma ihåg. 

Min kusin som arbetar på en känd akademi gav mig ett bra tips. Han sa att språket är ett arv, nästan som en nyfångad fisk som man måste blanda i en gryta. Det engelska ordet other kan översättas till "andra". Den enda regeln är att ha en livlig avslutning och en tydlig slutsats. Siffran är uppe i hundra regler, men jag kände att jag började förstå dem. "Jag skulle föredra att ta en rast nu och betala för lite fika," sa jag."""

core_words = [
    "begrepp", "påstående", "ruta", "diskutera", "stryka under", "bibliotek", 
    "fördel", "reduktion", "konjunktion", "komparativ", "kurskompis", "skriftlig", 
    "muntlig", "poängtera", "subjekt", "obestämd form", "asssimilation", "bisats", 
    "huvudsats", "repetera", "nyckelord", "nackdel", "bestämd form", "reflexiv", 
    "sammanfatta", "avslutning", "akademi", "slutsats", "prepostion", "supinum", 
    "imperativ", "ordkunkskapsövning", "subjunktion", "ordlista", "vokal", 
    "direkt tal", "konsonant", "ordkunskap", "stavelse"
]

glue_words = [
    "lapp", "så många som möjligt", "kusin", "svag", "livlig", "siffran är uppe i", 
    "föreslå", "nyfångad", "bestå av", "Har du lust att…?", "föredra", "betala", 
    "arv", "betona", "bevisa", "skicklig", "other", "enda", "Vad säger du?", 
    "blanda i", "klämdag"
]

target_mappings = [
    # Core
    ("begrepp", "begrepp"),
    ("påstående", "påstående"),
    ("ruta", "ruta"),
    ("diskutera", "diskutera"),
    ("stryka under", "stryka under"),
    ("bibliotek", "bibliotek"),
    ("fördel", "fördel"),
    ("reduktion", "reduktion"),
    ("konjunktion", "konjunktion"),
    ("komparativ", "komparativ"),
    ("kurskompis", "kurskompis"),
    ("skriftlig", "skriftlig"),
    ("muntlig", "muntlig"),
    ("poängtera", "poängterade"),
    ("subjekt", "subjekt"),
    ("obestämd form", "obestämd form"),
    ("asssimilation", "asssimilation"),
    ("bisats", "bisats"),
    ("huvudsats", "huvudsats"),
    ("repetera", "repetera"),
    ("nyckelord", "nyckelord"),
    ("nackdel", "nackdel"),
    ("bestämd form", "bestämd form"),
    ("reflexiv", "reflexiv"),
    ("sammanfatta", "sammanfatta"),
    ("avslutning", "avslutning"),
    ("akademi", "akademi"),
    ("slutsats", "slutsats"),
    ("prepostion", "prepostion"),
    ("supinum", "supinum"),
    ("imperativ", "imperativ"),
    ("ordkunkskapsövning", "ordkunkskapsövning"),
    ("subjunktion", "subjunktion"),
    ("ordlista", "ordlista"),
    ("vokal", "vokal"),
    ("direkt tal", "direkt tal"),
    ("konsonant", "konsonant"),
    ("ordkunskap", "ordkunskap"),
    ("stavelse", "stavelse"),

    # Glue
    ("lapp", "lapp"),
    ("så många som möjligt", "så många som möjligt"),
    ("kusin", "kusin"),
    ("svag", "svag"),
    ("livlig", "livlig"),
    ("siffran är uppe i", "Siffran är uppe i"),
    ("föreslå", "föreslå"),
    ("nyfångad", "nyfångad"),
    ("bestå av", "bestå av"),
    ("Har du lust att…?", "Har du lust att…?"),
    ("föredra", "föredra"),
    ("betala", "betala"),
    ("arv", "arv"),
    ("betona", "betona"),
    ("bevisa", "bevisa"),
    ("skicklig", "skicklig"),
    ("other", "other"),
    ("enda", "enda"),
    ("Vad säger du?", "Vad säger du?"),
    ("blanda i", "blanda i"),
    ("klämdag", "klämdag")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if " " in word_in_sentence or "." in word_in_sentence or "?" in word_in_sentence or "…" in word_in_sentence or "," in word_in_sentence:
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
    "article_id": "art_10",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('course/sfid/phase2/article_10.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
