import json

with open("./course/sfid/phase1/master_dictionary.json", "r") as f:
    master = json.load(f)["words"]

with open("./course/sfid/phase3/data/chunks/keys_2.json", "r") as f:
    keys = json.load(f)

# Let's inspect all keys and classify them with pure, clean rules:

# Non-Swedish / English PDF leftovers:
ENGLISH = {"about", "book", "climate", "Sami"}

# PDF hyphenated fragment:
FRAGMENTS = {"fylle-"}

# Full sentences, questions, dialogue lines, exclamations, or fragments with punctuation / quotes / brackets / math
# EXCEPT if it is a standard compound word with hyphen like "röd- och vitrandig" or "berg -och dalbana"
SENTENCES_PUNCT = {
    "Brukar du mysa?", "varifrån?", "faktum är att", "Visst låter det kul?", "puss puss",
    "inte…förrän", "Vet du när bussarna går?", "Vet du om?", "Jag skulle vilja veta hur…",
    "Vet du inte varför…?", "Vem frågade efter dig?", "Vad hände igår?", "Vad gjorde jag igår?",
    "Vet du vem som frågade efter dig?", "Vet du vad jag gjorde igår…?", "Jag har ingen aning om…",
    "Ska vi ta en fika?", "Jag kan tyvärr inte idag.", "Läget?", "Jo, det är helt okej.", "Du då?",
    "Det är fint?", "Kom igen!", "Jag har inte ett öre.", "Det ordnar sig.", "Okej då.",
    "Har du lust att…?", "Vad sägs om att…?", "Ska vi…?", "Tjaaa… jag vet inte rikitigt.",
    "Vet du vad som hände igår?", "Istället för att…", "Hur kommer det sig att…?",
    "”en sån” = vardagligt för en sådan", "f.kr. Före Kristus", "e.kr. Efter Kristus",
    "Det är inte sant!", "Va?! Du skojar!", "Helt otroligt!", "Det hade jag ingen aning om.",
    "fram till år…", "så… som möjligt", "Det sägs att…", "överdriv!", "Har du hört vad XX gjort?",
    "Vet du vad jag har läst?", "Visste du att…?", "Har du hört talas om …?", "Nähä!",
    "massmediet, massmedier, massmedierna)", "Vad har hänt?", "Vad tänker du på?", "Tänker ni…",
    "Tror du att…?", "Vad tänker du göra när…?", "se upp!", "–Hej! Det var länge sedan!",
    "–Jo, det är bara bra.", "–Själv då?", "Jaha, då ska vi se …", "Jag vet inte riktigt.",
    "Det var hemskt trevligt.", "Du kommer inte att tro dina öron!", "Vi får väl se.",
    "Hur dum får man vara?", "Jo, det är sant!", "Jo, jag lovar!", "Filmen handlar om…",
    "Filmen utspelar sig i", "Filmen bygger på en bok av…", "Filmen bygger på en verklig händelse.",
    "I slutet…", "”Det sjunde inseglet”", "”Fanny och Alexander”", "”Sommaren med Monica”",
    "”Den svenska synden”", "den här typen av …", "under senare delen av…", "en skam för …",
    "Har du ätit det någon gång?", "Nej, det har jag aldrig gjort!", "Det låter hemskt!"
}

# Pure Adverbs (Grammatical part of speech: Adverb)
ADVERBS = {
    "därmed", "dessutom", "verkligen", "äntligen", "förresten", "jo", "jämt",
    "nuförtiden", "istället", "efteråt", "i övermorgon", "genast", "redan",
    "så småningom", "emellertid", "dit", "förr", "någonsin", "exakt",
    "vidare", "nästan", "dock", "därför", "borta", "särskilt", "annars",
    "inte längre", "just det", "därpå", "hittills", "därför"
}

# Pure Prepositions & Conjunctions & Subjunctions & Pronouns & Numbers
PREPOSITIONS_CONJUNCTIONS_PRONOUNS = {
    "vid", "inuti", "inför", "hos", "mellan", "genom", "under", "per", "medan",
    "fastän", "tills", "ifall", "förrän", "även om", "genom att", "alltså", "samt",
    "om", "eller", "varannan", "allihop", "var och en", "var sin", "detta", "en",
    "denna", "dessa", "någonstans", "vem", "vad", "hur", "alla", "någon", "ingenting",
    "ingen", "femtio", "vartannat"
}

# Multi-word Prepositional / Adverbial phrases / Fixed non-noun/verb/adj clauses:
PHRASES_TO_REJECT = {
    "i centrum", "på första plats", "i allmänhet", "sedan dess", "i alla tider",
    "istället för", "strax utanför", "hemma hos", "inom parentes", "av olika slag",
    "en viss tid", "ingen annanstans", "strax innan", "på senare tid", "mot slutet av",
    "tack vare", "till en början", "vid kontakt med", "direkt efter", "i vintras",
    "under lång tid", "i knät", "meter över havet", "till ytan", "i princip",
    "per dygn", "på det sättet", "till fots", "lugn och ro", "mitt itu", "en mängd",
    "naturlig storlek", "någon gång", "10 år gammal", "historiskt sett", "känd för att ha",
    "Ju … desto", "hela dagen", "för skojs skull", "den här veckan", "som vanligt",
    "råttan i pizzan", "morgonen därpå", "lika stor som", "en tredjedel så stort som",
    "form av", "i längden", "inte se klok ut", "göra som man vill", "närma sig med stora steg",
    "för länge sedan", "fler och fler", "på order av", "sten efter sten", "tvåkilos",
    "ena", "även kallad", "året runt", "… för sig", "variant av", "en anledning till",
    "gjord av", "stora delar av", "något helt annat", "bakad på", "en typ av",
    "långt in på nätterna", "komma ifrån", "pricka in", "lika lön för lika arbete",
    "rätt till", "ett parti schack", "göra en paus", "vem som är vem", "precis som",
    "en annan gång", "Det passar bra.", "för några dagar sedan", "i måndags",
    "senast på fredag", "nästan aldrig", "inte på flera månader", "flera gånger i veckan",
    "vartannat år", "i somras"
}

# Valid Nouns, Verbs, and Adjectives that might have participial or compound form:
# e.g. godkänd (adj), övrig (adj), riven (adj), tärnad (adj), ugnsgräddad (adj), vispad (adj),
# röd- och vitrandig (adj), berg -och dalbana (noun), nära släkt (adj/noun phrase), etc.

accepted = []
rejected = []

for w in keys:
    wc = w.strip()
    if wc in ENGLISH:
        rejected.append((wc, "ENGLISH_WORD"))
    elif wc in FRAGMENTS:
        rejected.append((wc, "FRAGMENT"))
    elif wc in SENTENCES_PUNCT:
        rejected.append((wc, "SENTENCE_OR_PUNCT"))
    elif wc in ADVERBS:
        rejected.append((wc, "ADVERB"))
    elif wc in PREPOSITIONS_CONJUNCTIONS_PRONOUNS:
        rejected.append((wc, "PREP_CONJ_PRON_NUM"))
    elif wc in PHRASES_TO_REJECT:
        rejected.append((wc, "PHRASE_TO_REJECT"))
    else:
        accepted.append(wc)

print(f"Total evaluated: {len(keys)}")
print(f"Accepted (Nouns, Verbs, Adjectives): {len(accepted)}")
print(f"Rejected: {len(rejected)}")

