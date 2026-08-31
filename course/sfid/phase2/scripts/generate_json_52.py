import json
import re

text = """"Vad gör du där?" ropade min pappa när han kom in i rummet. Jag var mitt uppe i en tyst tanke, jag satt och försökte filosofera över min hemliga dröm om framtiden. Det fanns en stark framtidstro inom mig. "Jag försöker leta efter ett gammalt paket som jag tappat bort," svarade jag. 
"Du kommer inte att tro dina öron!" fortsatte pappa med stor förvåning i rösten. 

En ordförande från en internationell förening hade just ringt. Min gamla farbror, som egentligen jobbade med grafisk formgivning och ofta reste för att skaffa kontakter, hade skickat ett märkligt brev. Farbror var en mycket lugn nordbo, närmare bestämt en stolt norrman. Han hade i sin ungdom ibland arbetat som försöksperson i olika studier, och var ofta en central huvudperson i familjens mest dramatiska historier.

Vi började prata om vår stora språkfamilj och glädjen i att bevara vårt modersmål. Jag försökte minnas när min far och mor alltid sa att ett djupt intresse för språk måste ligga i släkten. Men min farbror hade en helt annan anledning att höra av sig nu. Dessutom hade min systerdotter och en annan dotter till min bror kommit för att lyssna. 

Farbror hade tydligen ingått ett viktigt avtal med en känd japan om att ge bort en unik vänskapsgåva, en sällsynt nejlika, men han hade sagt en liten vit lögn om dess egentliga ursprung. Farbror var i vanliga fall mycket noga med att aldrig flacka med blicken när han talade, utan han ville tvärtom alltid möta blicken tryggt. Han brukade stolt säga: "Man måste alltid kunna lita på mig." Han kände emellertid nu en djup skam över lögnen och han hade börjat känna skuld.

"Det är en skam för … ja, för hela vår familj," sa min pappa, fast han förmodligen överdrev lite. Han sa att det kändes som en väldigt feg lögn. Det var såklart inte ett hemskt brott, absolut inte hets mot folkgrupp, men ändå fel. Pappa ville absolut inte strida med farbror, men det fanns ju en tydlig orsak till att jag var lite besviken på honom. 

Min pappa bad oss att hjälpa till att servera kaffe och försöka komma överens om hur vi skulle beskriva detta för farbror när han väl kom tillbaka. "Vi får försöka göra det bästa av något som är tråkigt," sa jag. Vår huvudfråga var hur vi skulle kunna få honom att släppa sin tunga ångest. Vi ville att han skulle känna sig älskad trots sitt misstag. Även om man känner att man har kniven mot sin hals, ska man inte döma för snabbt, tyckte vår kloka talare till mor."""

core_words = [
    "vänskapsgåva", "huvudperson", "framtidstro", "nejlika", "avtal", 
    "ordförande", "hets mot folkgrupp", "mor", "systerdotter", "besviken", 
    "far", "dotter", "nordbo", "språkfamilj", "modersmål", "ligga i släkten", 
    "farbror", "norrman", "anledning", "lögn", "lita på", "en skam för …", 
    "känna skuld", "Du kommer inte att tro dina öron!", "förvåning", "älskad", 
    "komma överens", "skam", "vit lögn", "strida", "orsak", "flacka med blicken", 
    "försöksperson", "japan", "lugn", "tanke", "pappa", "hjälpa"
]

glue_words = [
    "internationell", "filosofera", "Vad gör du där?", "leta efter", "emellertid", 
    "detta", "talare", "beskriva", "noga", "hals", "tillbaka", "skaffa kontakter", 
    "möta blicken", "minnas", "paket", "servera", "grafisk formgivning", "släppa", 
    "utan", "dröm", "huvudfråga", "göra det bästa av något"
]

target_mappings = [
    # Core
    ("vänskapsgåva", "vänskapsgåva"),
    ("huvudperson", "huvudperson"),
    ("framtidstro", "framtidstro"),
    ("nejlika", "nejlika"),
    ("avtal", "avtal"),
    ("ordförande", "ordförande"),
    ("hets mot folkgrupp", "hets mot folkgrupp"),
    ("mor", "mor"),
    ("systerdotter", "systerdotter"),
    ("besviken", "besviken"),
    ("far", "far"),
    ("dotter", "dotter"),
    ("nordbo", "nordbo"),
    ("språkfamilj", "språkfamilj"),
    ("modersmål", "modersmål"),
    ("ligga i släkten", "ligga i släkten"),
    ("farbror", "farbror"),
    ("norrman", "norrman"),
    ("anledning", "anledning"),
    ("lögn", "lögn"),
    ("lita på", "lita på"),
    ("en skam för …", "en skam för …"),
    ("känna skuld", "känna skuld"),
    ("Du kommer inte att tro dina öron!", "Du kommer inte att tro dina öron!"),
    ("förvåning", "förvåning"),
    ("älskad", "älskad"),
    ("komma överens", "komma överens"),
    ("skam", "skam"),
    ("vit lögn", "vit lögn"),
    ("strida", "strida"),
    ("orsak", "orsak"),
    ("flacka med blicken", "flacka med blicken"),
    ("försöksperson", "försöksperson"),
    ("japan", "japan"),
    ("lugn", "lugn"),
    ("tanke", "tanke"),
    ("pappa", "pappa"),
    ("hjälpa", "hjälpa"),

    # Glue
    ("internationell", "internationell"),
    ("filosofera", "filosofera"),
    ("Vad gör du där?", "Vad gör du där?"),
    ("leta efter", "leta efter"),
    ("emellertid", "emellertid"),
    ("detta", "detta"),
    ("talare", "talare"),
    ("beskriva", "beskriva"),
    ("noga", "noga"),
    ("hals", "hals"),
    ("tillbaka", "tillbaka"),
    ("skaffa kontakter", "skaffa kontakter"),
    ("möta blicken", "möta blicken"),
    ("minnas", "minnas"),
    ("paket", "paket"),
    ("servera", "servera"),
    ("grafisk formgivning", "grafisk formgivning"),
    ("släppa", "släppa"),
    ("utan", "utan"),
    ("dröm", "dröm"),
    ("huvudfråga", "huvudfråga"),
    ("göra det bästa av något", "göra det bästa av något")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if " " in word_in_sentence or "." in word_in_sentence or "?" in word_in_sentence or "!" in word_in_sentence or "…" in word_in_sentence or "”" in word_in_sentence or "-" in word_in_sentence or "–" in word_in_sentence or "/" in word_in_sentence or ")" in word_in_sentence or "," in word_in_sentence or "=" in word_in_sentence:
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
    "step_id": "relationer_känslor",
    "step_title": "Relationer & Känslor",
    "article_id": "art_52",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('course/sfid/phase2/article_52.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
