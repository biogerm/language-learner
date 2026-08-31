import json
import re

text = """I kalla januari träffade jag en typisk hurtbulle. Han verkade född för att röra på sig. Varje morgon, jämt och helt utan uppehåll, brukade han jogga i skogen. Hans motto var: "Ju … desto!" vilket för honom betydde: ju snabbare, desto friskare. Han hade bestämt sig för att sätta upp ett stort mål och springa ett maraton. Han älskade att vara aktiv och ville komma ut för att bygga upp sin uthållighet, sin styrka och sin snabbhet. Han kunde vara duktig på att köra trettio armhävningar i sträck. Trots att han var smal var han mycket stark och alltid pigg. 

Han trodde aldrig att han skulle bli intagen på ett sjukhus. Han var registrerad på ett privat gym som säkert tjänade en miljard, eftersom branschen var enorm. Han skötte sina matvanor perfekt och drack absolut ingen alkohol, han var alltså aldrig berusad. Han gillade att intervjua sina vänner och giva dem träningsråd. Han visste hur man kunde rädda en ond rygg med rätt skydd, och hur en snabb uppfräschning kunde överraska kroppen positivt. Han älskade att känna sig fräsch och vägrade att lukta illa även om han var svettig.

Men en dag hände något som fick honom att fatta att hälsa är skört. Han skulle tyvärr bli tvungen att vila. Han blev plötsligt biten av en hund som var rabies-smittad! Han blev snabbt smittad och fick en allvarlig infektion. Det var inte som en vanlig allergi, utan kroppen reagerade som vid en kraftig allergichock med svår hosta. Smärtan spred sig i varje nerv. Han började lida enormt. Hans lidande var hemskt och han fick till och med en partiell ansiktsförlamning. 

Han fick genomgå en lång behandling och var ofta stressad över förlorad inkomst efter sin första karensdag. Han kunde inte aktivera sig som vanligt. Efter vad som kändes som ett helt sekel i sängen, kunde han till slut korsa en osynlig linje tillbaka till hälsa. Han menar nu att förmågan att stanna upp ibland symboliserar sann visdom."""

core_words = [
    "miljard", "rygg", "maraton", "skydd", "jogga", "stressad", "hurtbulle", 
    "alkohol", "snabbhet", "pigg", "uthållighet", "styrka", "vila", "armhävning", 
    "svettig", "smal", "röra på sig", "matvana", "köra", "fräsch", "lukta illa", 
    "nerv", "lida", "aktivera sig", "karensdag", "uppfräschning", "intagen", 
    "ansiktsförlamning", "rabies-smittad", "behandling", "allergichock", 
    "lidande", "hosta", "berusad", "infektion", "smittad", "allergi"
]

glue_words = [
    "linje", "komma ut", "bli tvungen", "född", "registrerad", "sätta upp", 
    "som vanligt", "vara duktig på", "aktiv", "privat", "fatta", "januari", 
    "sekel", "intervjua", "enorm", "rädda", "Ju … desto", "symbolisera", 
    "överraska", "giva", "typisk", "jämt", "uppehåll"
]

target_mappings = [
    # Core
    ("miljard", "miljard"),
    ("rygg", "rygg"),
    ("maraton", "maraton"),
    ("skydd", "skydd"),
    ("jogga", "jogga"),
    ("stressad", "stressad"),
    ("hurtbulle", "hurtbulle"),
    ("alkohol", "alkohol"),
    ("snabbhet", "snabbhet"),
    ("pigg", "pigg"),
    ("uthållighet", "uthållighet"),
    ("styrka", "styrka"),
    ("vila", "vila"),
    ("armhävning", "armhävningar"),
    ("svettig", "svettig"),
    ("smal", "smal"),
    ("röra på sig", "röra på sig"),
    ("matvana", "matvanor"),
    ("köra", "köra"),
    ("fräsch", "fräsch"),
    ("lukta illa", "lukta illa"),
    ("nerv", "nerv"),
    ("lida", "lida"),
    ("aktivera sig", "aktivera sig"),
    ("karensdag", "karensdag"),
    ("uppfräschning", "uppfräschning"),
    ("intagen", "intagen"),
    ("ansiktsförlamning", "ansiktsförlamning"),
    ("rabies-smittad", "rabies-smittad"),
    ("behandling", "behandling"),
    ("allergichock", "allergichock"),
    ("lidande", "lidande"),
    ("hosta", "hosta"),
    ("berusad", "berusad"),
    ("infektion", "infektion"),
    ("smittad", "smittad"),
    ("allergi", "allergi"),

    # Glue
    ("linje", "linje"),
    ("komma ut", "komma ut"),
    ("bli tvungen", "bli tvungen"),
    ("född", "född"),
    ("registrerad", "registrerad"),
    ("sätta upp", "sätta upp"),
    ("som vanligt", "som vanligt"),
    ("vara duktig på", "vara duktig på"),
    ("aktiv", "aktiv"),
    ("privat", "privat"),
    ("fatta", "fatta"),
    ("januari", "januari"),
    ("sekel", "sekel"),
    ("intervjua", "intervjua"),
    ("enorm", "enorm"),
    ("rädda", "rädda"),
    ("Ju … desto", "Ju … desto"),
    ("symbolisera", "symboliserar"),
    ("överraska", "överraska"),
    ("giva", "giva"),
    ("typisk", "typisk"),
    ("jämt", "jämt"),
    ("uppehåll", "uppehåll")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if base == "smittad":
        start = text.find("snabbt smittad") + 7
    elif base == "lida":
        start = text.find("började lida") + 8
    elif base == "fräsch":
        start = text.find("känna sig fräsch") + 10
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
    "article_id": "art_26",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('course/sfid/phase2/article_26.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
