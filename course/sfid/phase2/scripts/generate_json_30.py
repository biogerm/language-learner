import json
import re

text = """Hoppas ni alla/du mår bra! Min vardag ser nog ut som något helt annat än din. Jag jobbar hemifrån i ett gammalt boende som brukade vara ett vandrarhem. Byggnaden är lika stor som ett litet palats, eller kanske mer som ett stort lantställe. I en mysig lokal nära en sluss sitter jag i mina mjukiskläder. Jag brukar dagdrömma och ta en paus med kaffe och en hård skorpa i mitt vardagsrum. Ibland brukar jag snusa.

På vintern, t.ex. i kall februari, brukar jag stanna hemma. Jag är lite som en städare och försöker hålla ren miljö överallt. Jag gillar inte att släpa på tunga kassar från ett möbelvaruhus eller handla i ett stressigt köpcentrum i centrum. I ett svenskt folkhem fanns det i alla tider en tradition att stanna hemma hos familjen. En myskväll (”en sån” = vardagligt för en sådan mysig kväll) är vad jag brukar leva för. 

Folk i mitt grannland kan ha olika syn på ett roligt nöjesliv. Åtta av tio vill gå ut och roa sig. De vill besöka ett fint societetshus under en varm sommarmånad och dansa långt in på nätterna. De gillar att annonsera sina fester. Där finns det något för alla, men ibland kan någon vara hal som en ål och luras. Tystnad kan vara bättre.

Själv känner jag mig ibland som en gammal riddare som måste hindra kaoset. En gång kom en exotisk skorpion in i mitt sommarställe. Det var tre år i rad som jag bodde där under semestern. Jag var helt halvsovande och var tvungen att vifta bort den när den sprang runt på golvet. 

Nu är det äntligen söndag. Ikväll tänker jag göra av med lite energi. Kanske ska jag debutera som författare. Jag lärde mig nyss en ny sats om grammatik och hur man använder futurum. Jag brukar alltid hålla upp dörren för nya möjligheter i livet."""

core_words = [
    "hemifrån", "vardag", "vandrarhem", "städare", "boende", "hålla upp dörren", 
    "lantställe", "skorpion", "halvsovande", "i centrum", "mjukiskläder", 
    "stanna hemma", "hemma hos", "myskväll", "”en sån” = vardagligt för en sådan", 
    "möbelvaruhus", "skorpa", "handla", "hålla ren", "köpcentrum", "futurum", 
    "folkhem", "snusa", "tre år i rad", "riddare", "paus", "dagdrömma", 
    "sommarställe", "sats", "leva för", "nöjesliv", "något för alla", 
    "societetshus", "sommarmånad", "något helt annat", "långt in på nätterna", 
    "ikväll", "vardagsrum"
]

glue_words = [
    "Hoppas ni alla/du mår bra!", "äntligen", "hal som en ål", "i alla tider", 
    "palats", "runt", "släpa", "sluss", "t.ex.", "annonsera", "söndag", 
    "februari", "lokal", "göra av med", "åtta av tio", "grannland", "tystnad", 
    "vifta", "lika stor som", "debutera", "hindra", "ha olika syn på"
]

target_mappings = [
    # Core
    ("hemifrån", "hemifrån"),
    ("vardag", "vardag"),
    ("vandrarhem", "vandrarhem"),
    ("städare", "städare"),
    ("boende", "boende"),
    ("hålla upp dörren", "hålla upp dörren"),
    ("lantställe", "lantställe"),
    ("skorpion", "skorpion"),
    ("halvsovande", "halvsovande"),
    ("i centrum", "i centrum"),
    ("mjukiskläder", "mjukiskläder"),
    ("stanna hemma", "stanna hemma"),
    ("hemma hos", "hemma hos"),
    ("myskväll", "myskväll"),
    ("”en sån” = vardagligt för en sådan", "”en sån” = vardagligt för en sådan"),
    ("möbelvaruhus", "möbelvaruhus"),
    ("skorpa", "skorpa"),
    ("handla", "handla"),
    ("hålla ren", "hålla ren"),
    ("köpcentrum", "köpcentrum"),
    ("futurum", "futurum"),
    ("folkhem", "folkhem"),
    ("snusa", "snusa"),
    ("tre år i rad", "tre år i rad"),
    ("riddare", "riddare"),
    ("paus", "paus"),
    ("dagdrömma", "dagdrömma"),
    ("sommarställe", "sommarställe"),
    ("sats", "sats"),
    ("leva för", "leva för"),
    ("nöjesliv", "nöjesliv"),
    ("något för alla", "något för alla"),
    ("societetshus", "societetshus"),
    ("sommarmånad", "sommarmånad"),
    ("något helt annat", "något helt annat"),
    ("långt in på nätterna", "långt in på nätterna"),
    ("ikväll", "Ikväll"),
    ("vardagsrum", "vardagsrum"),

    # Glue
    ("Hoppas ni alla/du mår bra!", "Hoppas ni alla/du mår bra!"),
    ("äntligen", "äntligen"),
    ("hal som en ål", "hal som en ål"),
    ("i alla tider", "i alla tider"),
    ("palats", "palats"),
    ("runt", "runt"),
    ("släpa", "släpa"),
    ("sluss", "sluss"),
    ("t.ex.", "t.ex."),
    ("annonsera", "annonsera"),
    ("söndag", "söndag"),
    ("februari", "februari"),
    ("lokal", "lokal"),
    ("göra av med", "göra av med"),
    ("åtta av tio", "Åtta av tio"),
    ("grannland", "grannland"),
    ("tystnad", "Tystnad"),
    ("vifta", "vifta"),
    ("lika stor som", "lika stor som"),
    ("debutera", "debutera"),
    ("hindra", "hindra"),
    ("ha olika syn på", "ha olika syn på")
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
    "step_id": "vardagsliv",
    "step_title": "Vardagsliv",
    "article_id": "art_30",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('course/sfid/phase2/article_30.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
