import json

with open("./course/sfid/phase1/master_dictionary.json", "r") as f:
    master = json.load(f)["words"]

with open("./course/sfid/phase3/data/chunks/keys_2.json", "r") as f:
    keys = json.load(f)

# Let's write rules that precisely distinguish:
# 1. Sentences / Clauses / Questions / Dialogue fragments
# 2. English words / fragments
# 3. Pure Adverbs, Conjunctions, Subjunctions, Prepositions, Pronouns, Numerals
# 4. Multi-word non-verb/non-noun phrases
# 5. Nouns, Verbs, Adjectives (including participial forms, compound nouns, phrasal verbs)

def analyze(word):
    w = word.strip()
    en = master.get(w, {}).get("en", "").lower()

    # Rule 1: English words in the dataset mistakenly kept
    if w in ["about", "book", "climate", "Sami"]:
        return False, "English word"

    # Rule 2: Prefixes / Fragments
    if w.endswith("-") and not w in ["röd- och vitrandig", "berg -och dalbana"]:
        return False, "Hyphenated fragment"

    # Rule 3: Sentences, Questions, Dialogue phrases
    if any(c in w for char_list in ["?", "!", "…", "”", "="] for c in char_list) or w.startswith("–") or w.startswith("”"):
        return False, "Punctuation/Sentence/Dialogue"

    # Specific clause/sentence strings without punctuation
    if w in [
        "faktum är att", "puss puss", "Jag kan tyvärr inte idag.", "Jo, det är helt okej.",
        "Du då?", "Det är fint?", "Jag har inte ett öre.", "Det ordnar sig.", "Okej då.",
        "Tjaaa… jag vet inte rikitigt.", "Hur kommer det sig att…", "mer eller mindre",
        "f.kr. Före Kristus", "e.kr. Efter Kristus", "10 år gammal", "Det är inte sant!",
        "historiskt sett", "Det sägs att…", "Nähä!", "massmediet, massmedier, massmedierna)",
        "–Hej! Det var länge sedan!", "just det", "–Jo, det är bara bra.", "–Själv då?",
        "Jaha, då ska vi se …", "Det passar bra.", "för några dagar sedan", "i måndags",
        "senast på fredag", "nästan aldrig", "inte på flera månader", "flera gånger i veckan",
        "vartannat år", "i somras", "Jag vet inte riktigt.", "Det var hemskt trevligt.",
        "känd för att ha", "Ju … desto", "hela dagen", "för skojs skull", "en skam för …",
        "den här veckan", "Du kommer inte att tro dina öron!", "Vi får väl se.", "som vanligt",
        "Hur dum får man vara?", "råttan i pizzan", "Jo, det är sant!", "Jo, jag lovar!",
        "morgonen därpå", "lika stor som", "en tredjedel så stort som", "form av",
        "i längden", "inte se klok ut", "per dygn", "på det sättet", "göra som man vill",
        "närma sig med stora steg"
    ]:
        return False, "Sentence / Clause / Idiom phrase"

    # Prepositional / Adverbial phrases
    if w in [
        "i centrum", "på första plats", "i allmänhet", "sedan dess", "i alla tider",
        "istället för", "strax utanför", "hemma hos", "inom parentes", "av olika slag",
        "en viss tid", "ingen annanstans", "strax innan", "på senare tid", "mot slutet av",
        "tack vare", "till en början", "vid kontakt med", "direkt efter", "i vintras",
        "under lång tid", "i knät", "meter över havet", "till ytan", "i princip",
        "fram till år…", "vid"
    ]:
        return False, "Prepositional / Adverbial phrase"

    # Conjunctions & Subjunctions
    if w in ["medan", "fastän", "tills", "ifall", "förrän", "även om", "genom att", "inte…förrän", "alltså", "annars", "subjunktioner"]:
        return False, "Conjunction / Subjunction"

    # Pronouns & Determiners
    if w in ["varannan", "allihop", "var och en", "var sin", "detta", "en", "denna", "dessa", "någonstans"]:
        return False, "Pronoun / Determiner"

    # Pure Adverbs (words that function only or primarily as adverbs)
    if w in [
        "därmed", "dessutom", "verkligen", "äntligen", "förresten", "jo", "jämt",
        "nuförtiden", "istället", "efteråt", "i övermorgon", "sist", "genast", "redan",
        "så småningom", "emellertid", "dit", "förr", "någonsin", "exakt", "säkert",
        "vidare", "annars", "nästan", "dock", "därför", "borta"
    ]:
        return False, "Adverb"

    # Prepositions
    if w in ["vid", "inuti", "inför", "hos", "mellan", "genom", "under"]:
        # Note: check if single preposition
        if w in ["vid", "inuti", "inför"]:
            return False, "Preposition"

    return True, "ACCEPT"

accepted_list = []
rejected_list = []

for i, w in enumerate(keys):
    acc, reason = analyze(w)
    tr = master.get(w, {}).get("en", "")
    if acc:
        accepted_list.append((i, w, tr))
    else:
        rejected_list.append((i, w, tr, reason))

print(f"Total keys: {len(keys)}")
print(f"Accepted: {len(accepted_list)}")
print(f"Rejected: {len(rejected_list)}")

print("\n=== REJECTED ITEMS AUDIT ===")
for idx, (i, w, tr, reason) in enumerate(rejected_list):
    print(f"{idx+1:3d}. [{i:4d}] {w:<35} | {reason:<30} | {tr}")

