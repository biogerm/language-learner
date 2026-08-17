import json

with open("./course/sfid/phase1/master_dictionary.json", "r") as f:
    master = json.load(f)["words"]

with open("./course/sfid/phase3/data/chunks/keys_2.json", "r") as f:
    keys = json.load(f)

# Categories to reject:
# 1. Punctuation / Sentences / Dialogue / Quotes / Ellipsis
# 2. English words ("about", "book", "climate", "Sami")
# 3. PDF fragments ("fylle-")
# 4. Pure adverbs (därmed, dessutom, verkligen, äntligen, förresten, jo, jämt, nuförtiden, istället, efteråt, i övermorgon, genast, redan, så småningom, emellertid, dit, förr, någonsin, exakt, säkert, vidare, nästan, dock, därför, borta, särskilt, annars)
# 5. Prepositions (vid, inuti, inför, hos, mellan, genom, under, per)
# 6. Conjunctions & Subjunctions (medan, fastän, tills, ifall, förrän, även om, genom att, inte…förrän, alltså, annars, samt)
# 7. Pronouns & Determiners (varannan, allihop, var och en, var sin, detta, en, denna, dessa, någonstans, vem, vad, hur)
# 8. Fixed non-noun/non-verb prepositional & adverbial phrases (i centrum, på första plats, i allmänhet, sedan dess, i alla tider, istället för, strax utanför, hemma hos, inom parentes, av olika slag, en viss tid, ingen annanstans, strax innan, på senare tid, mot slutet av, tack vare, till en början, vid kontakt med, direkt efter, i vintras, under lång tid, i knät, meter över havet, till ytan, i princip, fram till år…, per dygn, på det sättet, till fots, lugn och ro, mitt itu, en mängd, naturlig storlek, någon gång)

ADVERBS = {
    "därmed", "dessutom", "verkligen", "äntligen", "förresten", "jo", "jämt",
    "nuförtiden", "istället", "efteråt", "i övermorgon", "genast", "redan",
    "så småningom", "emellertid", "dit", "förr", "någonsin", "exakt", "säkert",
    "vidare", "nästan", "dock", "därför", "borta", "särskilt", "annars", "dessutom",
    "istället", "inte längre", "just det", "därpå"
}

PREPOSITIONS = {
    "vid", "inuti", "inför", "hos", "mellan", "genom", "under", "per"
}

CONJUNCTIONS_SUBJUNCTIONS = {
    "medan", "fastän", "tills", "ifall", "förrän", "även om", "genom att",
    "inte…förrän", "alltså", "annars", "samt", "om", "eller"
}

PRONOUNS_DETERMINERS = {
    "varannan", "allihop", "var och en", "var sin", "detta", "en", "denna", "dessa",
    "någonstans", "vem", "vad", "hur", "alla", "någon", "ingenting", "ingen"
}

ENGLISH_WORDS = {
    "about", "book", "climate", "Sami"
}

EXACT_REJECT_PHRASES = {
    "i centrum", "på första plats", "i allmänhet", "sedan dess", "i alla tider",
    "istället för", "strax utanför", "hemma hos", "inom parentes", "av olika slag",
    "en viss tid", "ingen annanstans", "strax innan", "på senare tid", "mot slutet av",
    "tack vare", "till en början", "vid kontakt med", "direkt efter", "i vintras",
    "under lång tid", "i knät", "meter över havet", "till ytan", "i princip",
    "fram till år…", "per dygn", "på det sättet", "till fots", "lugn och ro",
    "mitt itu", "en mängd", "naturlig storlek", "någon gång", "f.kr. Före Kristus",
    "e.kr. Efter Kristus", "10 år gammal", "historiskt sett", "så… som möjligt",
    "känd för att ha", "Ju … desto", "hela dagen", "för skojs skull", "en skam för …",
    "den här veckan", "som vanligt", "råttan i pizzan", "morgonen därpå",
    "lika stor som", "en tredjedel så stort som", "form av", "i längden",
    "inte se klok ut", "göra som man vill", "närma sig med stora steg",
    "för länge sedan", "fler och fler", "på order av", "sten efter sten",
    "tvåkilos", "ena", "även kallad", "året runt", "… för sig", "variant av",
    "en anledning till", "den här typen av …", "gjord av", "tärnad",
    "stora delar av", "övrig", "något helt annat", "bakad på", "ugnsgräddad",
    "vispad", "en typ av", "långt in på nätterna", "femtio", "komma ifrån",
    "pricka in", "Har du ätit det någon gång?", "Nej, det har jag aldrig gjort!",
    "Det låter hemskt!", "lika lön för lika arbete", "rätt till", "godkänd",
    "av olika slag", "en viss tid", "att göra något dumt", "mat och dryck",
    "nära släkt", "under senare delen av…", "puss puss", "faktum är att",
    "visst låter det kul?", "överdriv!", "Nähä!", "massmediet, massmedier, massmedierna)",
    "se upp!", "–Hej! Det var länge sedan!", "just det", "–Jo, det är bara bra.",
    "–Själv då?", "Jaha, då ska vi se …", "Det passar bra.", "för några dagar sedan",
    "i måndags", "senast på fredag", "nästan aldrig", "inte på flera månader",
    "flera gånger i veckan", "vartannat år", "i somras", "Jag vet inte riktigt.",
    "Det var hemskt trevligt.", "Du kommer inte att tro dina öron!", "Vi får väl se.",
    "Hur dum får man vara?", "Jo, det är sant!", "Jo, jag lovar!",
    "Filmen handlar om…", "Filmen utspelar sig i", "Filmen bygger på en bok av…",
    "Filmen bygger på en verklig händelse.", "I slutet…", "”Det sjunde inseglet”",
    "”Fanny och Alexander”", "”Sommaren med Monica”", "”Den svenska synden”",
    "ett parti schack", "göra en paus", "vem som är vem", "precis som"
}

filtered_keys = []
rejected_keys = []

for w in keys:
    w_clean = w.strip()
    
    # 1. Punctuation / Sentences / Dialogue
    if any(c in w_clean for c in ["?", "!", "…", "”", "="]) or w_clean.startswith("–") or w_clean.startswith("”"):
        rejected_keys.append((w_clean, "SENTENCE_OR_PUNCTUATION"))
        continue
        
    # 2. English words
    if w_clean in ENGLISH_WORDS:
        rejected_keys.append((w_clean, "ENGLISH_WORD"))
        continue
        
    # 3. Fragment
    if w_clean.endswith("-") or w_clean.startswith("-"):
        rejected_keys.append((w_clean, "FRAGMENT"))
        continue
        
    # 4. Adverbs
    if w_clean in ADVERBS:
        rejected_keys.append((w_clean, "ADVERB"))
        continue
        
    # 5. Prepositions
    if w_clean in PREPOSITIONS:
        rejected_keys.append((w_clean, "PREPOSITION"))
        continue
        
    # 6. Conjunctions / Subjunctions
    if w_clean in CONJUNCTIONS_SUBJUNCTIONS:
        rejected_keys.append((w_clean, "CONJUNCTION_SUBJUNCTION"))
        continue

    # 7. Pronouns
    if w_clean in PRONOUNS_DETERMINERS:
        rejected_keys.append((w_clean, "PRONOUN"))
        continue

    # 8. Fixed non-N/V/A phrases
    if w_clean in EXACT_REJECT_PHRASES:
        rejected_keys.append((w_clean, "REJECTED_PHRASE"))
        continue
        
    # Passed all checks -> NOUN, VERB, or ADJECTIVE!
    filtered_keys.append(w_clean)

print(f"Original total keys in keys_2.json: {len(keys)}")
print(f"Filtered keys (Nouns, Verbs, Adjectives): {len(filtered_keys)}")
print(f"Rejected keys: {len(rejected_keys)}")

