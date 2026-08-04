import json
import re

text = """Jag sa tack på förhand till min bästa vän för att han ville komma. Vi hade bestämt oss för att träffas och prata om relationer och hur vi brukar må. 
Han sa att han naturligtvis skulle ställa upp. Han var min bästa kompis, en person som jag alltid kunde chatta med. 

Vi började diskutera vad vi tyckte var viktigt. "Vad brukar du tycka bäst om i en familj?" frågade jag. "Och vad brukar du tycka sämst om?"
"Man bör gilla ärlighet," svarade han och såg glad ut. "Ett trevligt samtal är alltid bra, oavsett om det är djupt snack eller bara lite sportsnack."
"Jag håller med." svarade jag snabbt. "Och att man kan förlåta en annan vän. En stark vänskap är oerhört viktig för att man ska må bra och känna sig lycklig."

Vi pratade sedan om varför folk ibland väljer att skilja sig och plötsligt kan bli som en fiende till varandra. Det är alltid tråkigt när ett långt förhållande tar slut. Minnen från ett vackert bröllop eller en fin bröllopsdag kan kännas långt borta. Människor kan tyvärr skilja sig åt med tiden. Vissa väljer då att bo separat, och konflikter kan förekomma. "Då måste man ibland lämna över ansvaret och låta den andra personen gå fri från kritik," sa han. "Man ska inte behöva gå runt och känna ilska."

Han berättade därefter om sin egen flickvän. "Hon är en enorm djurvän, och vi försöker informera andra om en ny kampanj för utsatta djur, både stora och små."
"Är du riktigt kär i henne?" frågade jag.
"Ja, jag kan verkligen älska vårt lugna familjeliv. Men ibland kan jag ändå känna mig ensam när hon reser mycket."
"Det är ungefär så för mig också ibland," sa jag för att hålla med.
"Vi får väl se." sa han lugnt. "Det ordnar sig." 

Och efter det var vi båda trötta. Klockan var mycket, det var en jättesen kväll, och ungdomar utanför fönstret skrek ord med prefixet jätte- framför allt. Jag försökte vara tyst som en mus och började smyga mot dörren. 
"Du har tur som kan somna snabbt," log han. "Kärleken kommer att räcka långt, om man bara vågar vilja ha den."""

core_words = [
    "som", "prata", "behöva", "vilja", "tycka bäst om", "tycka sämst om", 
    "må", "må bra", "känna", "känna sig/mig", "familj", "gilla", "glad", 
    "snack", "sportsnack", "familjeliv", "lycklig", "tack på förhand", 
    "vän", "vänskap", "hålla med", "ensam", "ungefär så", "kompis", 
    "träffas", "skilja sig", "förlåta", "fiende", "djurvän", 
    "Jag håller med.", "chatta", "bröllop", "bröllopsdag", "bästa kompis", 
    "kär", "bästa vän", "flickvän", "älska"
]

glue_words = [
    "räcka", "till", "kampanj", "gå fri", "informera", "med tiden", 
    "slut", "naturligtvis", "jätte-", "Det ordnar sig.", "stora och små", 
    "separat", "tyst som en mus", "Vi får väl se.", "skilja sig åt", 
    "lämna över", "somna", "jättesen", "smyga", "förekomma", 
    "efter det", "tur"
]

target_mappings = [
    # Core
    ("som", "som"),
    ("prata", "prata"),
    ("behöva", "behöva"),
    ("vilja", "vilja"),
    ("tycka bäst om", "tycka bäst om"),
    ("tycka sämst om", "tycka sämst om"),
    ("må", "må"),
    ("må bra", "må bra"),
    ("känna", "känna"),
    ("känna sig/mig", "känna mig"),
    ("familj", "familj"),
    ("gilla", "gilla"),
    ("glad", "glad"),
    ("snack", "snack"),
    ("sportsnack", "sportsnack"),
    ("familjeliv", "familjeliv"),
    ("lycklig", "lycklig"),
    ("tack på förhand", "tack på förhand"),
    ("vän", "vän"),
    ("vänskap", "vänskap"),
    ("hålla med", "hålla med"),
    ("ensam", "ensam"),
    ("ungefär så", "ungefär så"),
    ("kompis", "kompis"),
    ("träffas", "träffas"),
    ("skilja sig", "skilja sig"),
    ("förlåta", "förlåta"),
    ("fiende", "fiende"),
    ("djurvän", "djurvän"),
    ("Jag håller med.", "Jag håller med."),
    ("chatta", "chatta"),
    ("bröllop", "bröllop"),
    ("bröllopsdag", "bröllopsdag"),
    ("bästa kompis", "bästa kompis"),
    ("kär", "kär"),
    ("bästa vän", "bästa vän"),
    ("flickvän", "flickvän"),
    ("älska", "älska"),

    # Glue
    ("räcka", "räcka"),
    ("till", "till"),
    ("kampanj", "kampanj"),
    ("gå fri", "gå fri"),
    ("informera", "informera"),
    ("med tiden", "med tiden"),
    ("slut", "slut"),
    ("naturligtvis", "naturligtvis"),
    ("jätte-", "jätte-"),
    ("Det ordnar sig.", "Det ordnar sig."),
    ("stora och små", "stora och små"),
    ("separat", "separat"),
    ("tyst som en mus", "tyst som en mus"),
    ("Vi får väl se.", "Vi får väl se."),
    ("skilja sig åt", "skilja sig åt"),
    ("lämna över", "lämna över"),
    ("somna", "somna"),
    ("jättesen", "jättesen"),
    ("smyga", "smyga"),
    ("förekomma", "förekomma"),
    ("efter det", "efter det"),
    ("tur", "tur")
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
    "article_id": "art_49",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('./course/sfid/phase2/article_49.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
