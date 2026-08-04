import json
import re

text = """Det fanns en affisch i vår vänthall som visade drömmen om god hälsa. På affischen stod det: "Varför inte? Du kan må toppklass!" Men i verkligheten är det ofta svårt. Min patient Per brukade komma från en tuff miljö. Han var, som han själv sa, en alkis /alkoholist och brukade missbruka en farlig drog över tid. Efter en olycka med en häst, där han nästan lyckades bryta nacken, låg han länge på vårt sjukhus. Han hade djupa sår på sin nacke, och en trasig led, särskilt sin vänstra fotled. Han fick byta ut flera trasiga tänder mot löständer.

"Vad ska du hålla på med nu?" frågade jag honom en gång. 
"Tjaaa… jag vet inte rikitigt." svarade han, och började harkla sig. Han berättade att olyckan var ett fylle- misstag eller något i den stilen. 

Han led också av en extrem trötthet. Han var faktiskt allergiker och var mycket allergisk mot viss onyttig mat, vilket ironiskt nog ledde till övervikt. Hans mage och hans mun kunde ibland svullna upp och hans tunga blev väldigt svullen. Ibland började det klia över hela hans huvud och han fick en svår huvudvärk. 

Han kände sig ofta deprimerad, och det var en allvarlig tid. Han sa att det kändes som om han hade fått pesten eller en väldigt farlig lunginflammation. Han hade hög feber och kunde knappt andas. Tvärtom mot vad han hade trott, fanns det ingen snabb medicin för att bota allting direkt.

Vi la upp ett tidsschema för att kunna genomföra hans behandling, och han fick stanna under säker uppsikt. "Det är bra att vaccinera sig mot säsongsinfluensan," sa jag. "Vi ska vaccinera dig imorgon." Det är viktigt genom att det hjälper oss att inte överföra smitta till andra patienter.

Förr i tiden fanns det mycket skräp och osanningar inom vården, och gamla myter kan leva kvar de senaste femtio åren, till exempel rykten om farlig abort. Men nu kan vi planera bättre i förväg och kanske kan man tänka sig en mycket ljusare framtid. Mot slutet av året var Per äntligen sugen på livet igen, efter cirka nio månader på kliniken."""

core_words = [
    "vaccinera sig mot", "vaccinera", "allergisk mot", "överföra", "harkla", 
    "huvudvärk", "övervikt", "onyttig", "bota", "bryta nacken", "andas", 
    "svullen", "sår", "huvud", "tunga", "feber", "fylle-", "svullna upp", "mun", 
    "allergiker", "nacke", "led", "missbruka", "löständer", "alkis /alkoholist", 
    "sugen", "fotled", "trötthet", "abort", "klia", "drog", "deprimerad", 
    "lunginflammation", "pesten"
]

glue_words = [
    "komma från", "Tjaaa… jag vet inte rikitigt.", "kanske", "toppklass", 
    "affisch", "drömmen om", "cirka", "femtio", "tidsschema", "allvarlig", 
    "tänka sig", "genomföra", "förr i tiden", "skräp", "i förväg", "leva kvar", 
    "häst", "något i den stilen", "hålla på med", "mot slutet av", "över tid", 
    "de senaste", "genom att", "tvärtom", "uppsikt", "Varför inte?"
]

target_mappings = [
    # Core
    ("vaccinera sig mot", "vaccinera sig mot"),
    ("vaccinera", "vaccinera"),
    ("allergisk mot", "allergisk mot"),
    ("överföra", "överföra"),
    ("harkla", "harkla"),
    ("huvudvärk", "huvudvärk"),
    ("övervikt", "övervikt"),
    ("onyttig", "onyttig"),
    ("bota", "bota"),
    ("bryta nacken", "bryta nacken"),
    ("andas", "andas"),
    ("svullen", "svullen"),
    ("sår", "sår"),
    ("huvud", "huvud"),
    ("tunga", "tunga"),
    ("feber", "feber"),
    ("fylle-", "fylle-"),
    ("svullna upp", "svullna upp"),
    ("mun", "mun"),
    ("allergiker", "allergiker"),
    ("nacke", "nacke"),
    ("led", "led"),
    ("missbruka", "missbruka"),
    ("löständer", "löständer"),
    ("alkis /alkoholist", "alkis /alkoholist"),
    ("sugen", "sugen"),
    ("fotled", "fotled"),
    ("trötthet", "trötthet"),
    ("abort", "abort"),
    ("klia", "klia"),
    ("drog", "drog"),
    ("deprimerad", "deprimerad"),
    ("lunginflammation", "lunginflammation"),
    ("pesten", "pesten"),

    # Glue
    ("komma från", "komma från"),
    ("Tjaaa… jag vet inte rikitigt.", "Tjaaa… jag vet inte rikitigt."),
    ("kanske", "kanske"),
    ("toppklass", "toppklass"),
    ("affisch", "affisch"),
    ("drömmen om", "drömmen om"),
    ("cirka", "cirka"),
    ("femtio", "femtio"),
    ("tidsschema", "tidsschema"),
    ("allvarlig", "allvarlig"),
    ("tänka sig", "tänka sig"),
    ("genomföra", "genomföra"),
    ("förr i tiden", "Förr i tiden"),
    ("skräp", "skräp"),
    ("i förväg", "i förväg"),
    ("leva kvar", "leva kvar"),
    ("häst", "häst"),
    ("något i den stilen", "något i den stilen"),
    ("hålla på med", "hålla på med"),
    ("mot slutet av", "Mot slutet av"),
    ("över tid", "över tid"),
    ("de senaste", "de senaste"),
    ("genom att", "genom att"),
    ("tvärtom", "Tvärtom"),
    ("uppsikt", "uppsikt"),
    ("Varför inte?", "Varför inte?")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if base == "vaccinera":
        start = text.find("ska vaccinera dig") + 4
    elif base == "led":
        start = text.find("trasig led") + 7
    elif base == "huvud":
        start = text.find("hans huvud") + 5
    elif " " in word_in_sentence or "." in word_in_sentence or "?" in word_in_sentence or "!" in word_in_sentence or "…" in word_in_sentence or "”" in word_in_sentence or "-" in word_in_sentence or "–" in word_in_sentence or "/" in word_in_sentence or ")" in word_in_sentence or "," in word_in_sentence:
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
    "article_id": "art_27",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('./course/sfid/phase2/article_27.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
