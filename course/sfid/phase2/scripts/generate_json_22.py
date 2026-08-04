import json
import re

text = '''För några år sedan mådde jag väldigt dåligt. Jag hade problem med min vikt och jag fortsatte att gå upp i vikt. Jag var trött hela tiden, ibland helt dödstrött. Jag hade svårt att sova och det kändes som en parasit i min kropp. En läkare tvingade mig till och med att lägga in mig på ett sinnessjukhus på grund av risken för självmord efter en oavsiktlig överdos av medicin. Det var en hemsk tid. Jag fick ibland råd per brev, men inget verkade passa mig. 

Men en dag läste jag ett tips på en vägg intill sjukhuset: "Lyssna till ditt hjärta." Jag bestämde mig för att bli frisk och att det är viktigt att bry sig om sin hälsa. Jag ville inte bara sitta och slappa. Det var i samband med detta jag anmälde mig till en exotisk träningsresa. Evenemanget skulle äga rum i Spanien. 

Jag packade mina träningskläder och träningsskor. Där började ett nära samarbete med en sportig gyminstruktör. Han förklarade att all motion är nyttig. Han sa att "motienera" ger en hälsosam livsstil. Vi tränade i en serie av korta pass. Det var en motionsform som byggde på intensiv styrketräning. 

I början fick jag väldigt ont i ett knä och i varje muskel i mina ben. Ibland blev jag delvis döv av ansträngning, men jag lärde mig att stretcha efter varje träningspass. Fastän jag fick extrem träningsvärk, kändes det ändå bra att svettas och förbättra min kondition. Allt handlar inte bara om att träna stenhårt, man måste också koppla av. Att vila är inte en halvsanning – det är jätteviktigt!

Min form förbättrades mycket snabbare än jag någonsin sett. Pulsen var som lägst när vi mediterade. Vi lärde oss att lyssna på kroppen, som fungerar lite… för sig, på ett fantastiskt sätt. Om någon hade sagt att jag skulle träna i fin frack hade jag skrattat. Alla ville hänga med. När jag till slut bad om att få svar på vad hälsa kallas för, sa min tränare: "Det är livet."'''

core_words = [
    "passa", "träna", "trött", "dödstrött", "svettas", "kondition", "nyttig", 
    "kropp", "slappa", "träningsresa", "vikt", "gå upp i vikt", "pass", 
    "träningspass", "träningskläder", "sova", "frisk", "ont", "knä", "muskel", 
    "ben", "motion", "motionsform", "träningsvärk", "stretcha", "styrketräning", 
    "träningsskor", "motienera", "hälsosam", "koppla av", "gyminstruktör", 
    "sportig", "bry sig om", "Lyssna till ditt hjärta.", "överdos", "självmord", 
    "sinnessjukhus"
]

glue_words = [
    "exotisk", "per brev", "lyssna", "tvinga", "parasit", "äga rum", "sett", 
    "ändå", "lägst", "kallas för", "frack", "hänga med", "intill", 
    "i samband med", "få svar", "vägg", "delvis", "döv", "snabbare än", "serie", 
    "nära samarbete", "halvsanning", "… för sig"
]

target_mappings = [
    # Core
    ("passa", "passa"),
    ("träna", "träna"),
    ("trött", "trött"),
    ("dödstrött", "dödstrött"),
    ("svettas", "svettas"),
    ("kondition", "kondition"),
    ("nyttig", "nyttig"),
    ("kropp", "kropp"),
    ("slappa", "slappa"),
    ("träningsresa", "träningsresa"),
    ("vikt", "vikt"),
    ("gå upp i vikt", "gå upp i vikt"),
    ("pass", "pass"),
    ("träningspass", "träningspass"),
    ("träningskläder", "träningskläder"),
    ("sova", "sova"),
    ("frisk", "frisk"),
    ("ont", "ont"),
    ("knä", "knä"),
    ("muskel", "muskel"),
    ("ben", "ben"),
    ("motion", "motion"),
    ("motionsform", "motionsform"),
    ("träningsvärk", "träningsvärk"),
    ("stretcha", "stretcha"),
    ("styrketräning", "styrketräning"),
    ("träningsskor", "träningsskor"),
    ("motienera", "motienera"),
    ("hälsosam", "hälsosam"),
    ("koppla av", "koppla av"),
    ("gyminstruktör", "gyminstruktör"),
    ("sportig", "sportig"),
    ("bry sig om", "bry sig om"),
    ("Lyssna till ditt hjärta.", "Lyssna till ditt hjärta."),
    ("överdos", "överdos"),
    ("självmord", "självmord"),
    ("sinnessjukhus", "sinnessjukhus"),

    # Glue
    ("exotisk", "exotisk"),
    ("per brev", "per brev"),
    ("lyssna", "lyssna"),
    ("tvinga", "tvingade"),
    ("parasit", "parasit"),
    ("äga rum", "äga rum"),
    ("sett", "sett"),
    ("ändå", "ändå"),
    ("lägst", "lägst"),
    ("kallas för", "kallas för"),
    ("frack", "frack"),
    ("hänga med", "hänga med"),
    ("intill", "intill"),
    ("i samband med", "i samband med"),
    ("få svar", "få svar"),
    ("vägg", "vägg"),
    ("delvis", "delvis"),
    ("döv", "döv"),
    ("snabbare än", "snabbare än"),
    ("serie", "serie"),
    ("nära samarbete", "nära samarbete"),
    ("halvsanning", "halvsanning"),
    ("… för sig", "… för sig")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if base == "vikt":
        start = text.find("min vikt") + 4
    elif base == "kropp":
        start = text.find("min kropp") + 4
    elif base == "pass":
        start = text.find("korta pass") + 6
    elif base == "ben":
        start = text.find("mina ben") + 5
    elif base == "träna":
        start = text.find("att träna stenhårt") + 4
    elif base == "lyssna":
        start = text.find("att lyssna") + 4
    elif base == "motion":
        start = text.find("all motion") + 4
    elif " " in word_in_sentence or "." in word_in_sentence or "?" in word_in_sentence or "!" in word_in_sentence or "…" in word_in_sentence or "”" in word_in_sentence or "-" in word_in_sentence or "–" in word_in_sentence:
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
    "step_id": "hälsa_medicin",
    "step_title": "Hälsa & Medicin",
    "article_id": "art_22",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('./course/sfid/phase2/article_22.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
