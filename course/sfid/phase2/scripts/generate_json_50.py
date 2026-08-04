import json
import re

text = """Hej Maria!
Vet du om? Det är sant att tiderna förändras verkligen snabbt. Tidigt i morse drack jag kaffe i min varma morgonrock. Min pojkvän sa då att han ville gifta sig nästa år.
Vi har ett starkt förhållande och en väldigt bra relation, men vi pratar också om hur vanligt det tyvärr är med en skilsmässa. Folk vill umgås, men mycket är ändå inte som förr. Det blev plötsligt mycket prat om hans stora släkt och alla deras barn. Varje förälder vill ju alltid det bästa. Jag hoppas att vi får vara lyckliga. Han var gift tidigare, och hans före detta fru blev visst arg som ett bi när hon trodde att han hade träffat en ny älskare. Man kan ibland bli ilsken och behöva vänja min bror vid situationen, för det tar tid att vänja sig vid nya saker.

Under vår senaste långhelg åkte vi allihop upp till landet. Vi hade anställt en ung barnvakt till några små skolbarn från en annan barnfamilj. Barnen älskade gamla sagor. Vi brukade ofta påminna dem om berättelser som Rödluvan och vargen och även Peter och vargen. Kanske en av er också minns hur spännande det var? En riktig varg kan ju se farlig och rentav livsfarlig ut, med en imponerande stor mankhöjd. Om man möter en kan man behöva vända bilen snabbt eller vända sig om i skogen. Som tur är syns de ganska sällan i allmänhet. Vargen är ju hundens kända stamfader.

Sedan besökte vi en lokal älgfarm tillsammans. Deras absolut bästa säljargument var att besökare fick klappa älgarna under en regelbunden tid. Det är tydligen en expanderande turistnäring med en snabbt ökad popularitet. Det var tolv personer där samtidigt. Ingen kände sig rädd, med ett enda undantag. Det fanns en inofficiell regel där som sa att man måste ha en godkänd djurskötare med sig för att kunna kontrollera allt. 
Då kunde man plötsligt komma på att deras gamla valspråk var att djuren fortfarande ska ha full respekt. I slutet… av hela dagen var vi alla extremt trötta och nöjda. 

Hör av dig snart!
Puss och kram …
Kramar …"""

core_words = [
    "gifta sig", "skilsmässa", "som förr", "pojkvän", "barn", "förhållande", 
    "släkt", "umgås", "fru", "förälder", "hoppas", "älskare", "bror", "gift", 
    "prat", "Puss och kram …", "Kramar …", "barnvakt", "ilsken", "farlig", 
    "vänja", "vänja sig vid", "relation", "livsfarlig", "varg", "arg som ett bi", 
    "vända", "mankhöjd", "skolbarn", "i morse", "Rödluvan och vargen", 
    "Peter och vargen", "fortfarande", "vända sig om", "barnfamilj", 
    "säljargument", "morgonrock", "älgfarm"
]

glue_words = [
    "Hör av dig snart!", "godkänd", "i allmänhet", "valspråk", "I slutet…", 
    "långhelg", "regelbunden", "komma på", "påminna", "ganska", "stamfader", 
    "en av er", "inofficiell", "tiderna förändras", "allihop", "undantag", 
    "kontrollera", "man måste ha", "expanderande", "Vet du om?", "tolv", "ökad"
]

target_mappings = [
    # Core
    ("gifta sig", "gifta sig"),
    ("skilsmässa", "skilsmässa"),
    ("som förr", "som förr"),
    ("pojkvän", "pojkvän"),
    ("barn", "barn"),
    ("förhållande", "förhållande"),
    ("släkt", "släkt"),
    ("umgås", "umgås"),
    ("fru", "fru"),
    ("förälder", "förälder"),
    ("hoppas", "hoppas"),
    ("älskare", "älskare"),
    ("bror", "bror"),
    ("gift", "gift"),
    ("prat", "prat"),
    ("Puss och kram …", "Puss och kram …"),
    ("Kramar …", "Kramar …"),
    ("barnvakt", "barnvakt"),
    ("ilsken", "ilsken"),
    ("farlig", "farlig"),
    ("vänja", "vänja"),
    ("vänja sig vid", "vänja sig vid"),
    ("relation", "relation"),
    ("livsfarlig", "livsfarlig"),
    ("varg", "varg"),
    ("arg som ett bi", "arg som ett bi"),
    ("vända", "vända"),
    ("mankhöjd", "mankhöjd"),
    ("skolbarn", "skolbarn"),
    ("i morse", "i morse"),
    ("Rödluvan och vargen", "Rödluvan och vargen"),
    ("Peter och vargen", "Peter och vargen"),
    ("fortfarande", "fortfarande"),
    ("vända sig om", "vända sig om"),
    ("barnfamilj", "barnfamilj"),
    ("säljargument", "säljargument"),
    ("morgonrock", "morgonrock"),
    ("älgfarm", "älgfarm"),

    # Glue
    ("Hör av dig snart!", "Hör av dig snart!"),
    ("godkänd", "godkänd"),
    ("i allmänhet", "i allmänhet"),
    ("valspråk", "valspråk"),
    ("I slutet…", "I slutet…"),
    ("långhelg", "långhelg"),
    ("regelbunden", "regelbunden"),
    ("komma på", "komma på"),
    ("påminna", "påminna"),
    ("ganska", "ganska"),
    ("stamfader", "stamfader"),
    ("en av er", "en av er"),
    ("inofficiell", "inofficiell"),
    ("tiderna förändras", "tiderna förändras"),
    ("allihop", "allihop"),
    ("undantag", "undantag"),
    ("kontrollera", "kontrollera"),
    ("man måste ha", "man måste ha"),
    ("expanderande", "expanderande"),
    ("Vet du om?", "Vet du om?"),
    ("tolv", "tolv"),
    ("ökad", "ökad")
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
    "article_id": "art_50",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('./course/sfid/phase2/article_50.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
