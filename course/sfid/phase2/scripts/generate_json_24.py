import json
import re

text = """"I början av … ja, på 1900-talet, såg vår hälsovård helt annorlunda ut än idag," sa min gamla mormor. "Viss medicinsk kunskap har visserligen funnits sedan 500 f.kr. Före Kristus, men samhället har förändrats." Vi hade samlats i en vacker paviljong för att fira hennes födelsedag. Det blev ett gripande berättande om hennes långa liv. "Jo, jag lovar!" fortsatte hon ivrigt. "Tidigare var allt annat än lätt."

Hon hade arbetat inom svensk sjukvård under många år. Byggnaderna brukade ligga nära varandra på sjukhusområdet. I ett litet rum med en väldig lukt av rök och stark medicin, tog de hand om patienterna. Ibland fick de ge p-piller eller en smärtstillande tablett till kvinnorna. Om en kvinna var gravid och kände ångest, fick hon vila lite till. Man fick ofta kolla med en erfaren läkare innan någon fick gå över till en ny behandling.

"I en sameby i norr fanns en kvinna med ett allvarligt funktionshinder," mindes hon. "Hon fick ofta gå till fots ner för berget." Det blev en anledning till att staten ville bygga ut samhället. Politikerna skrev ett viktigt lagförslag, som senare blev en proposition, om allas rättighet till tandvård, barnomsorg och åldringsvård. Varje medborgare skulle ha rätt till bra vård, vilket var en enorm investering för vårt land. Målet var att folkets behov skulle uppfyllas.

"När jag var ung hade vi lagom mycket mat," skrattade hon när vi åt tillsammans. Vi åt ofta traditionellt paltbröd med olika tillbehör. En viktig ingrediens var ofta salt skinka. Men när jag fick ont i min mage blev min vanliga mat bortplockad. Vi åt sällan sötsaker, kanske lite god vaniljsås om vi hade tur. Min mormors fysiska skick var dåligt cirka fem år efter kriget. Då var tallrikarna sällan fyllda av färsk mat, utan ibland enbart fylld med varm soppa. En gång råkade hon få schampo i ögonen när hon tvättade sig, och höll på att ramla av sin pall! "Min skål var i alla fall helt fylld," mindes hon. 

Trots all brist på pengar försökte man år efter år hjälpa de sjuka från början till slut. Ett varmt hjärta kan ibland bota mycket. Om någon drabbades försökte man begrava oron och prata öppet. Efter rätt vård kunde de ofta gå tillbaka till det normala/vanliga."""

core_words = [
    "medicinsk", "berättande", "hälsovård", "sjukvård", "rök", "tandvård", 
    "barnomsorg", "åldringsvård", "funktionshinder", "tablett", "lagförslag", 
    "proposition", "ångest", "gravid", "lite till", "medicin", "paviljong", 
    "uppfyllas", "gå tillbaka till det normala/vanliga", "sameby", "fyllda av", 
    "ner för", "till fots", "år efter år", "en anledning till", "fylld med", 
    "tillbehör", "paltbröd", "ingrediens", "gå över till", "rätt till", "p-piller", 
    "vaniljsås", "mage", "hjärta", "fylld", "skinka"
]

glue_words = [
    "fem", "från början", "lagom", "tidigare", "f.kr. Före Kristus", "lukt", 
    "annat än", "öppet", "ligga nära varandra", "väldig", "bortplockad", "begrava", 
    "tillsammans", "skick", "schampo i ögonen", "kolla med", "investering", 
    "Jo, jag lovar!", "i början av …", "samlas", "ramla av", "brist på", "gripande"
]

target_mappings = [
    # Core
    ("medicinsk", "medicinsk"),
    ("berättande", "berättande"),
    ("hälsovård", "hälsovård"),
    ("sjukvård", "sjukvård"),
    ("rök", "rök"),
    ("tandvård", "tandvård"),
    ("barnomsorg", "barnomsorg"),
    ("åldringsvård", "åldringsvård"),
    ("funktionshinder", "funktionshinder"),
    ("tablett", "tablett"),
    ("lagförslag", "lagförslag"),
    ("proposition", "proposition"),
    ("ångest", "ångest"),
    ("gravid", "gravid"),
    ("lite till", "lite till"),
    ("medicin", "medicin"),
    ("paviljong", "paviljong"),
    ("uppfyllas", "uppfyllas"),
    ("gå tillbaka till det normala/vanliga", "gå tillbaka till det normala/vanliga"),
    ("sameby", "sameby"),
    ("fyllda av", "fyllda av"),
    ("ner för", "ner för"),
    ("till fots", "till fots"),
    ("år efter år", "år efter år"),
    ("en anledning till", "en anledning till"),
    ("fylld med", "fylld med"),
    ("tillbehör", "tillbehör"),
    ("paltbröd", "paltbröd"),
    ("ingrediens", "ingrediens"),
    ("gå över till", "gå över till"),
    ("rätt till", "rätt till"),
    ("p-piller", "p-piller"),
    ("vaniljsås", "vaniljsås"),
    ("mage", "mage"),
    ("hjärta", "hjärta"),
    ("fylld", "fylld"),
    ("skinka", "skinka"),

    # Glue
    ("fem", "fem"),
    ("från början", "från början"),
    ("lagom", "lagom"),
    ("tidigare", "Tidigare"),
    ("f.kr. Före Kristus", "f.kr. Före Kristus"),
    ("lukt", "lukt"),
    ("annat än", "annat än"),
    ("öppet", "öppet"),
    ("ligga nära varandra", "ligga nära varandra"),
    ("väldig", "väldig"),
    ("bortplockad", "bortplockad"),
    ("begrava", "begrava"),
    ("tillsammans", "tillsammans"),
    ("skick", "skick"),
    ("schampo i ögonen", "schampo i ögonen"),
    ("kolla med", "kolla med"),
    ("investering", "investering"),
    ("Jo, jag lovar!", "Jo, jag lovar!"),
    ("i början av …", "I början av …"),
    ("samlas", "samlats"),
    ("ramla av", "ramla av"),
    ("brist på", "brist på"),
    ("gripande", "gripande")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if base == "fylld":
        start = text.find("fylld,")
    elif base == "medicin":
        start = text.find("stark medicin") + 6
    elif base == "rök":
        start = text.find("lukt av rök") + 8
    elif " " in word_in_sentence or "." in word_in_sentence or "?" in word_in_sentence or "!" in word_in_sentence or "…" in word_in_sentence or "”" in word_in_sentence or "-" in word_in_sentence or "–" in word_in_sentence or "/" in word_in_sentence:
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
    "article_id": "art_24",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('./course/sfid/phase2/article_24.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
