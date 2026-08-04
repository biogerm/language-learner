import json
import re

text = """En fredag pratade min lärare, en trevlig engelsman, mycket om svensk politik och historia, om förr och nu. "Hänger du med?" frågade han och såg på oss.
"Redan som ung hörde jag ofta en berättelse om hur gamla länder fungerade," började han. "Vissa länder hade länge ett mäktigt styre under en bestämd kejsarinna. På den tiden skulle man kröna en härskare under pompa och ståt för att hen skulle sitta på en tron. Ibland fanns det också en religiös ledare, som en katolsk påve, eller en representant för en lutheransk trosinriktning inom vår tidiga kristendom."

Han berättade att det ofta var farligt att lägga sig i makten på den tiden. En okänd utlänning eller en politisk motståndare kunde snabbt hamna på en galgbacke för en blodig avrättning. Man kunde också bli tvingad att rulla ihop sig i fosterställning om någon hotade att skjuta en tung järnkula mot en under ett krig. "Hur dum får man vara?" sa en klasskamrat och började stirra på en hemsk bild i en tidning om gamla vapen. "En tvåkilos kula är ju jättetung och livsfarlig."

Sedan ändrades samhället drastiskt. Vi gick från manuellt arbete till industriell masstillverkning och en ökad konsumtion i sig, mycket tack vare tidig globalisering. Vårt eget land fick ett nytt politiskt system. Ett lokalt förbund från varje län samlades för att skapa en demokratisk stat. Idag styrs mycket lagstiftning av en riksdagsledamot i Stockholm och varje lokal ledamot i våra olika kommittéer. En viktig representant för folket bör ha en modern syn på allas jämlikhet, helt oavsett kön eller sexuell läggning. Samtidigt kan en stor folkomröstning eller en mer vanlig omröstning handla om väldigt svåra frågor. Även tolv år senare minns man kanske ett historiskt beslut om till exempel ett nationellt spritförbud och hur svårt det var att hålla reda på alla olika politiska åsikter. 

Idag diskuterar vi moderna faror som rasism och högerextremism. Ibland går en känd kvinnlig partiledare ut i ett stort nyhetsprogram för att påminna om vikten av ett politiskt samförstånd mellan två stora politiska block. Då krävs det ofta en stark koalition. Man försöker gemensamt bekämpa farliga idéer som extrem kommuism. Om folket vill klaga, väljer de ofta att demonstrera i en fredlig demonstration. Det stora torget brukar vara nere på stan, och det fungerar som en mycket bra samlingsplats. 

Nyligen hörde jag en schweizisk politiker som var envis som en åsna inför ett nytt lagförslag om framtidens familjer. Han diskuterade bland annat rätten att adoptera små barn från ett utsatt barnhem. Det visade tydligt att politik alltid är och förblir viktigt för vår vardag."""

core_words = [
    "representant", "block", "masstillverkning", "kejsarinna", "koalition", 
    "högerextremism", "samförstånd", "tvåkilos", "styre", "konsumtion", 
    "schweizisk", "skjuta", "barnhem", "järnkula", "län", "globalisering", 
    "kvinnlig", "sexuell läggning", "demonstration", "lutheransk", 
    "demonstrera", "spritförbud", "engelsman", "förbund", "omröstning", 
    "trosinriktning", "kommuism", "kröna", "folkomröstning", "utlänning", 
    "påve", "riksdagsledamot", "kristendom", "nyhetsprogram", "galgbacke", 
    "avrättning", "adoptera", "ledamot", "tron", "kön"
]

glue_words = [
    "Hur dum får man vara?", "tolv år senare", "envis som en åsna", 
    "som ung", "tidning", "vara nere på", "berättelse", "bör ha", 
    "stirra", "i sig", "inför", "hålla reda på", "fredag", 
    "Hänger du med?", "fosterställning", "samlingsplats", "oss", 
    "förr och nu", "lägga sig i", "påminna om"
]

target_mappings = [
    # Core
    ("representant", "representant"),
    ("block", "block"),
    ("masstillverkning", "masstillverkning"),
    ("kejsarinna", "kejsarinna"),
    ("koalition", "koalition"),
    ("högerextremism", "högerextremism"),
    ("samförstånd", "samförstånd"),
    ("tvåkilos", "tvåkilos"),
    ("styre", "styre"),
    ("konsumtion", "konsumtion"),
    ("schweizisk", "schweizisk"),
    ("skjuta", "skjuta"),
    ("barnhem", "barnhem"),
    ("järnkula", "järnkula"),
    ("län", "län"),
    ("globalisering", "globalisering"),
    ("kvinnlig", "kvinnlig"),
    ("sexuell läggning", "sexuell läggning"),
    ("demonstration", "demonstration"),
    ("lutheransk", "lutheransk"),
    ("demonstrera", "demonstrera"),
    ("spritförbud", "spritförbud"),
    ("engelsman", "engelsman"),
    ("förbund", "förbund"),
    ("omröstning", "omröstning"),
    ("trosinriktning", "trosinriktning"),
    ("kommuism", "kommuism"),
    ("kröna", "kröna"),
    ("folkomröstning", "folkomröstning"),
    ("utlänning", "utlänning"),
    ("påve", "påve"),
    ("riksdagsledamot", "riksdagsledamot"),
    ("kristendom", "kristendom"),
    ("nyhetsprogram", "nyhetsprogram"),
    ("galgbacke", "galgbacke"),
    ("avrättning", "avrättning"),
    ("adoptera", "adoptera"),
    ("ledamot", "ledamot"),
    ("tron", "tron"),
    ("kön", "kön"),

    # Glue
    ("Hur dum får man vara?", "Hur dum får man vara?"),
    ("tolv år senare", "tolv år senare"),
    ("envis som en åsna", "envis som en åsna"),
    ("som ung", "som ung"),
    ("tidning", "tidning"),
    ("vara nere på", "vara nere på"),
    ("berättelse", "berättelse"),
    ("bör ha", "bör ha"),
    ("stirra", "stirra"),
    ("i sig", "i sig"),
    ("inför", "inför"),
    ("hålla reda på", "hålla reda på"),
    ("fredag", "fredag"),
    ("Hänger du med?", "Hänger du med?"),
    ("fosterställning", "fosterställning"),
    ("samlingsplats", "samlingsplats"),
    ("oss", "oss"),
    ("förr och nu", "förr och nu"),
    ("lägga sig i", "lägga sig i"),
    ("påminna om", "påminna om")
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
    "step_id": "samhälle_politik",
    "step_title": "Samhälle & Politik",
    "article_id": "art_48",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('./course/sfid/phase2/article_48.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
