import json
import re

text = """Mannen på vår lilla ö

Det sägs att… man lätt kan ha det tråkigt på landsbygden. Jag bor på en härlig ö, och jag är stolt över att vara en lantis. Här finns en man som brukar bjuda in till middag under sitt stora, blå tak. Han är känd som byns flintis /flintskallig gubbe. 

Han var gift med en trevlig kvinna, och deras långa äktenskap kändes som en sjungande vacker dröm. Hon flyttade och sedan dess känner han en stor sorg. Det var synd om honom, tyckte många grannar.

Han ville laga god mat för alla och försöka locka gäster för att skapa en bra stämning i huset. Han sa att faktum är att han verkligen ville vara en hedersman och hjälpa till med byns utveckling. Man kan kalla honom en fantastisk hedersman på många sätt. Hans starka identitet byggde på att alltid tala sanning. Han sa ofta: "Förstår du? Man får aldrig skvallra om sina grannar." Han kunde ge råd till exakt alla som behövde det. Han brukade till och med tända ett ljus för dem han tänkt på och ville beundra.

Men en ny man flyttade till byn. Han var en riktig mytoman och en farlig lögnare. Han ville bara luras och bråka. Han var väldigt snabbtänkt och verkade seriös på ytan, men var ganska otrevlig inuti. Han började genast skruva på sig när man ställde djupa frågor. Hans konstiga beteende var mycket irriterande, men ändå blev man tyvärr lite lockad av hans vilda historier. "Hur snabbt?" frågade vi ofta när han stolt berättade en osannolik variant av en händelse. Han var en icke-rökare, och han ville aldrig hålla kopplad sin aggressiva hund. 

Han var inte alls kontrollerad. Det kunde ganska snart visa sig att hans ord inte alls var en självklar sanning. Vi slutade helt att tro på hans berättelser. Han tyckte om att använda engelska uttryck och pratade ofta med ord som "one’s" för att verka internationell. 

"Är det en acceptabel prognos för vår by?" sa ordföranden med en djup suck. Allt var definitivt inte frid och fröjd längre. Han ville ofta lova att vara snäll, men han blev bara sur när vi ifrågasatte honom. 
"Helt otroligt!" sa vi. 
Han ville vara lik en god människa, och vi bar på ett litet hopp om att han skulle ändra sig. Men han vågade inte stanna, och därför blev en obligatorisk flytt det enda valet."""

core_words = [
    "ha det tråkigt", "flintis /flintskallig", "sjungande", "bjuda", 
    "stämning", "lantis", "identitet", "hedersman", "suck", "synd", "sur", 
    "lova", "irriterande", "ge råd", "beundra", "mytoman", "sorg", "lögnare", 
    "tala sanning", "snabbtänkt", "äktenskap", "kontrollerad", "luras", 
    "lockad", "acceptabel", "skruva på sig", "frid och fröjd", "skvallra", 
    "visa sig", "osannolik", "otrevlig", "seriös", "hedersman"
]

glue_words = [
    "vara lik", "tak", "Förstår du?", "blå", "obligatorisk", "Hur snabbt?", 
    "Det sägs att…", "Helt otroligt!", "ljus", "locka", "tro", "one’s", 
    "variant", "gift med", "prognos", "sedan dess", "laga", "våga", "med", 
    "hålla kopplad", "självklar", "hopp", "faktum är att", "icke-rökare", 
    "tänkt", "härlig", "ö"
]

target_mappings = [
    # Core
    ("ha det tråkigt", "ha det tråkigt"),
    ("flintis /flintskallig", "flintis /flintskallig"),
    ("sjungande", "sjungande"),
    ("bjuda", "bjuda"),
    ("stämning", "stämning"),
    ("lantis", "lantis"),
    ("identitet", "identitet"),
    ("hedersman", "hedersman"),
    ("suck", "suck"),
    ("synd", "synd"),
    ("sur", "sur"),
    ("lova", "lova"),
    ("irriterande", "irriterande"),
    ("ge råd", "ge råd"),
    ("beundra", "beundra"),
    ("mytoman", "mytoman"),
    ("sorg", "sorg"),
    ("lögnare", "lögnare"),
    ("tala sanning", "tala sanning"),
    ("snabbtänkt", "snabbtänkt"),
    ("äktenskap", "äktenskap"),
    ("kontrollerad", "kontrollerad"),
    ("luras", "luras"),
    ("lockad", "lockad"),
    ("acceptabel", "acceptabel"),
    ("skruva på sig", "skruva på sig"),
    ("frid och fröjd", "frid och fröjd"),
    ("skvallra", "skvallra"),
    ("visa sig", "visa sig"),
    ("osannolik", "osannolik"),
    ("otrevlig", "otrevlig"),
    ("seriös", "seriös"),
    ("hedersman", "hedersman"),

    # Glue
    ("vara lik", "vara lik"),
    ("tak", "tak"),
    ("Förstår du?", "Förstår du?"),
    ("blå", "blå"),
    ("obligatorisk", "obligatorisk"),
    ("Hur snabbt?", "Hur snabbt?"),
    ("Det sägs att…", "Det sägs att…"),
    ("Helt otroligt!", "Helt otroligt!"),
    ("ljus", "ljus"),
    ("locka", "locka"),
    ("tro", "tro"),
    ("one’s", "one’s"),
    ("variant", "variant"),
    ("gift med", "gift med"),
    ("prognos", "prognos"),
    ("sedan dess", "sedan dess"),
    ("laga", "laga"),
    ("våga", "våga"),
    ("med", "med"),
    ("hålla kopplad", "hålla kopplad"),
    ("självklar", "självklar"),
    ("hopp", "hopp"),
    ("faktum är att", "faktum är att"),
    ("icke-rökare", "icke-rökare"),
    ("tänkt", "tänkt"),
    ("härlig", "härlig"),
    ("ö", "ö")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if " " in word_in_sentence or "." in word_in_sentence or "?" in word_in_sentence or "!" in word_in_sentence or "…" in word_in_sentence or "”" in word_in_sentence or "-" in word_in_sentence or "–" in word_in_sentence or "/" in word_in_sentence or ")" in word_in_sentence or "," in word_in_sentence or "=" in word_in_sentence or "’" in word_in_sentence:
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
    "article_id": "art_56",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('./course/sfid/phase2/article_56.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
