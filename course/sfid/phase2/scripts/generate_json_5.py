import json
import re

text = """När man talar om arbetsliv, tänker många på en bra karriär. Först tänkte jag bli bankdirektör och jobba i en stor finansvärld. Men min yrkesplan ändrades gradvis. "Vad jobbar hon med?" frågade en vän. Jag berättade att jag hade fått ett nytt jobb i en mörk källarfabrik. Det var en mycket ovanlig sak att välja en industri framför att sitta på kontor.

En vanlig arbetsdag är ofta lång och jobbig. Ibland känner jag att det är dålig miljö att arbeta i en så tuff arbetsmiljö. Men jag gillar att byta uppgifter och jag har alltid sällskap av varje kollega. Man kan också få nya vänner genom kollegor. Vi är alla med i samma fackförbund, vilket är viktigt. De hjälper oss att finansiera kurser och säkerställa en rimlig arbetstid. Vi vill inte ha en extrem arbetsvecka. Vi har också en chef som ibland vill visa vem som bestämmer. En produktchef besöker oss ofta och säger vad vi ska göra. Men vi är en arbetsam grupp och försöker skapa balans.

Att vara högavlönad är inte lätt i denna bransch. Jag är lågavlönad jämfört med skogsindustri eller tung gruvindustri. Vi betalar också en viss skatt på allt vi kan tjäna. Vår lön räcker oftast, men ibland måste jag jobba extra. Vi har flera maskiner och vi pratade med vår arbetskamrat och frågade om en maskin: "Vad fick ni ge för det?" Maskinerna måste funka bra för att undvika arbetslöshet.

När vi äntligen är ledig, försöker vi njuta av en helt arbetsfri helg. Det är skönt att komma bort från arbetet. Efter en halv dag av vila är det dags för hushållsarbete. Det är tungt att Komma hem från jobbet. Men jag är glad över mitt yrke och hoppas få en bra praktik framöver. Hela min familj tycker att det är roligt, så länge jag inte går ner mig i stress. Jag hörde min vän säga att man ska älska sitt arbete."""

core_words = [
    "jobbig", "jobb", "jobba", "ledig", "hushållsarbete", "arbeta", "arbetsfri", "arbetsdag", 
    "industri", "genom kollegor", "sällskap", "Komma hem från jobbet.", "Vad jobbar hon med?", 
    "karriär", "bankdirektör", "praktik", "finansiera", "gruvindustri", "skogsindustri", 
    "kollega", "finansvärld", "fackförbund", "arbetsam", "tjäna", "arbetslöshet", "skatt", 
    "Vad fick ni ge för det?", "lön", "funka", "arbetskamrat", "yrke", "yrkesplan", 
    "högavlönad", "lågavlönad", "arbetstid", "arbetsmiljö", "visa vem som bestämmer", 
    "arbetsvecka", "jobba extra", "produktchef", "källarfabrik"
]

glue_words = [
    "säga", "komma", "hela", "byta", "stor", "först", "ner", "dålig", "när", "flera", 
    "alla", "man", "lång", "sak", "balans", "gradvis", "halv", "viss", "ovanlig"
]

target_mappings = [
    # Core
    ("jobbig", "jobbig"),
    ("jobb", "jobb"),
    ("jobba", "jobba"),
    ("ledig", "ledig"),
    ("hushållsarbete", "hushållsarbete"),
    ("arbeta", "arbeta"),
    ("arbetsfri", "arbetsfri"),
    ("arbetsdag", "arbetsdag"),
    ("industri", "industri"),
    ("genom kollegor", "genom kollegor"),
    ("sällskap", "sällskap"),
    ("Komma hem från jobbet.", "Komma hem från jobbet."),
    ("Vad jobbar hon med?", "Vad jobbar hon med?"),
    ("karriär", "karriär"),
    ("bankdirektör", "bankdirektör"),
    ("praktik", "praktik"),
    ("finansiera", "finansiera"),
    ("gruvindustri", "gruvindustri"),
    ("skogsindustri", "skogsindustri"),
    ("kollega", "kollega"),
    ("finansvärld", "finansvärld"),
    ("fackförbund", "fackförbund"),
    ("arbetsam", "arbetsam"),
    ("tjäna", "tjäna"),
    ("arbetslöshet", "arbetslöshet"),
    ("skatt", "skatt"),
    ("Vad fick ni ge för det?", "Vad fick ni ge för det?"),
    ("lön", "lön"),
    ("funka", "funka"),
    ("arbetskamrat", "arbetskamrat"),
    ("yrke", "yrke"),
    ("yrkesplan", "yrkesplan"),
    ("högavlönad", "högavlönad"),
    ("lågavlönad", "lågavlönad"),
    ("arbetstid", "arbetstid"),
    ("arbetsmiljö", "arbetsmiljö"),
    ("visa vem som bestämmer", "visa vem som bestämmer"),
    ("arbetsvecka", "arbetsvecka"),
    ("jobba extra", "jobba extra"),
    ("produktchef", "produktchef"),
    ("källarfabrik", "källarfabrik"),

    # Glue
    ("säga", "säga"),
    ("komma", "komma"),
    ("hela", "Hela"),
    ("byta", "byta"),
    ("stor", "stor"),
    ("först", "Först"),
    ("ner", "ner"),
    ("dålig", "dålig"),
    ("när", "När"),
    ("flera", "flera"),
    ("alla", "alla"),
    ("man", "man"),
    ("lång", "lång"),
    ("sak", "sak"),
    ("balans", "balans"),
    ("gradvis", "gradvis"),
    ("halv", "halv"),
    ("viss", "viss"),
    ("ovanlig", "ovanlig")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if base == "jobb":
        start = text.find("nytt jobb") + 5
    elif base == "jobba":
        start = text.find("och jobba i") + 4
    elif base == "komma":
        start = text.find("komma bort")
    else:
        if " " in word_in_sentence or "." in word_in_sentence or "?" in word_in_sentence:
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
    "article_id": "art_05",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('./course/sfid/phase2/article_5.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
