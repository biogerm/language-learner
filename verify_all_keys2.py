import json

with open("./course/sfid/phase1/master_dictionary.json", "r") as f:
    master = json.load(f)["words"]

with open("./course/sfid/phase3/data/chunks/keys_2.json", "r") as f:
    keys = json.load(f)

# Let's inspect words and check if they are Noun, Verb, or Adjective
# We will flag words that are prepositions, adverbs, conjunctions, pronouns, sentences, or English dictionary entries

def classify_word(word, translation):
    w = word.strip()
    tr = translation.lower()

    # Sentences, questions, phrases with special punctuation or punctuation marks
    if any(char in w for char in ["?", "!", "…", "”", "="]) or w.startswith("–") or w.startswith("”") or w.startswith("10 år") or w.startswith("1800-t") or w.startswith("1900-t") or w.startswith("1700-t"):
        if w not in ["1800-talet", "1900-talet", "1700-talet"]: # these century words are Nouns ("att leva på 1800-talet")
            return "REJECT_SENTENCE_OR_PUNCT"

    # Known English filler words in PDF
    if w in ["about", "book", "climate", "Sami"]:
        return "REJECT_ENGLISH"

    # Prefixes/fragments
    if w.endswith("-") or w.startswith("-"):
        return "REJECT_FRAGMENT"

    # Conjunctions / Subjunctions
    if w in ["medan", "fastän", "tills", "ifall", "förrän", "även om", "genom att", "inte…förrän", "alltså", "annars"]:
        return "REJECT_CONJUNCTION"

    # Pronouns / Determiners
    if w in ["varannan", "allihop", "var och en", "var sin", "detta", "en", "vilken"]:
        return "REJECT_PRONOUN"

    # Adverbs
    if w in ["därmed", "dessutom", "verkligen", "äntligen", "förresten", "jo", "jämt", "nuförtiden", "istället", "efteråt", "i övermorgon", "sist", "genast", "redan", "så småningom", "emellertid", "dit", "annorlunda", "förr", "någonsin"]:
        # Note: "genast", "redan", "så småningom", "emellertid", "dit", "någonsin" are adverbs!
        return "REJECT_ADVERB"

    # Prepositional / Adverbial phrases
    if w in [
        "i centrum", "på första plats", "i allmänhet", "sedan dess", "i alla tider", "istället för",
        "strax utanför", "hemma hos", "inom parentes", "av olika slag", "en viss tid", "ingen annanstans",
        "strax innan", "på senare tid", "mot slutet av", "tack vare", "till en början", "vid kontakt med",
        "direkt efter", "i vintras", "under lång tid", "i knät", "meter över havet", "till ytan",
        "i princip", "i längden", "per dygn", "på det sättet", "för skojs skull", "en skam för …",
        "den här veckan", "som vanligt", "råttan i pizzan", "morgonen därpå", "lika stor som",
        "en tredjedel så stort som", "form av", "nära släkt", "fram till år…", "historiskt sett",
        "så… som möjligt", "utbildad inom", "känd för att ha", "hela dagen", "förra veckan",
        "under senare delen av…", "f.kr. Före Kristus", "e.kr. Efter Kristus", "mat och dryck"
    ]:
        return "REJECT_PHRASE"

    # Sentences or full multi-word clause expressions without clear N/V/A identity
    if w in [
        "Brukar du mysa?", "faktum är att", "Visst låter det kul?", "puss puss",
        "Vet du när bussarna går?", "Vet du om?", "Jag skulle vilja veta hur…", "Vet du inte varför…?",
        "Vem frågade efter dig?", "Vad hände igår?", "Vad gjorde jag igår?", "Vet du vem som frågade efter dig?",
        "Vet du vad jag gjorde igår…?", "Jag har ingen aning om…", "Ska vi ta en fika?", "Jag kan tyvärr inte idag.",
        "Läget?", "Jo, det är helt okej.", "Du då?", "Det är fint?", "Kom igen!", "Jag har inte ett öre.",
        "Det ordnar sig.", "Okej då.", "Har du lust att…?", "Vad sägs om att…?", "Ska vi…?",
        "Tjaaa… jag vet inte rikitigt.", "Vet du vad som hände igår?", "Istället för att…",
        "Hur kommer det sig att…?", "”en sån” = vardagligt för en sådan", "mer eller mindre",
        "Det är inte sant!", "Va?! Du skojar!", "Helt otroligt!", "Det hade jag ingen aning om.",
        "Det sägs att…", "Har du hört vad XX gjort?", "Vet du vad jag har läst?", "Visste du att…?",
        "Har du hört talas om …?", "Nähä!", "massmediet, massmedier, massmedierna)", "Vad har hänt?",
        "Vad tänker du på?", "Tänker ni…", "Tror du att…?", "Vad tänker du göra när…?",
        "–Hej! Det var länge sedan!", "just det", "–Jo, det är bara bra.", "–Själv då?",
        "Jaha, då ska vi se …", "Det passar bra.", "för några dagar sedan", "i måndags",
        "senast på fredag", "nästan aldrig", "inte på flera månader", "flera gånger i veckan",
        "vartannat år", "i somras", "Jag vet inte riktigt.", "Det var hemskt trevligt.",
        "Ju … desto", "Du kommer inte att tro dina öron!", "Vi får väl se.",
        "Hur dum får man vara?", "Jo, det är sant!", "Jo, jag lovar!", "inte se klok ut"
    ]:
        return "REJECT_CLAUSE"

    return "ACCEPT"

accepted = []
rejected = []

for i, w in enumerate(keys):
    tr = master.get(w, {}).get("en", "")
    res = classify_word(w, tr)
    if res == "ACCEPT":
        accepted.append((i, w, tr))
    else:
        rejected.append((i, w, tr, res))

print(f"Total evaluated: {len(keys)}")
print(f"Accepted (Nouns, Verbs, Adjectives): {len(accepted)}")
print(f"Rejected: {len(rejected)}")

print("\n--- SAMPLE REJECTED ITEMS ---")
for i, w, tr, r in rejected[:40]:
    print(f"{i:4d}: {w:<35} | {r:<25} | {tr}")

print("\n--- SAMPLE ACCEPTED ITEMS ---")
for i, w, tr in accepted[:40]:
    print(f"{i:4d}: {w:<35} | {tr}")
