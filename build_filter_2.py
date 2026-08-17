import json
import re

with open("./course/sfid/phase1/master_dictionary.json", "r") as f:
    master = json.load(f)["words"]

with open("./course/sfid/phase3/data/chunks/keys_2.json", "r") as f:
    keys = json.load(f)

# List of known sentences, expressions, adverbs, prepositions, subjunctions, pronouns, english words to exclude
EXCLUDE_SET = {
    # Full sentences / questions / dialogues / interjections / phrases with punct
    "Brukar du mysa?", "varifrån?", "faktum är att", "Visst låter det kul?", "puss puss",
    "Vet du när bussarna går?", "Vet du om?", "Jag skulle vilja veta hur…", "Vet du inte varför…?",
    "Vem frågade efter dig?", "Vad hände igår?", "Vad gjorde jag igår?", "Vet du vem som frågade efter dig?",
    "Vet du vad jag gjorde igår…?", "Jag har ingen aning om…", "Ska vi ta en fika?", "Jag kan tyvärr inte idag.",
    "Läget?", "Jo, det är helt okej.", "Du då?", "Det är fint?", "Kom igen!", "Jag har inte ett öre.",
    "Det ordnar sig.", "Okej då.", "Har du lust att…?", "Vad sägs om att…?", "Ska vi…?",
    "Tjaaa… jag vet inte rikitigt.", "Vet du vad som hände igår?", "Istället för att…",
    "Hur kommer det sig att…?", "”en sån” = vardagligt för en sådan", "mer eller mindre",
    "under senare delen av…", "f.kr. Före Kristus", "e.kr. Efter Kristus", "10 år gammal",
    "Det är inte sant!", "Va?! Du skojar!", "Helt otroligt!", "Det hade jag ingen aning om.",
    "fram till år…", "historiskt sett", "så… som möjligt", "Det sägs att…",
    "Har du hört vad XX gjort?", "Vet du vad jag har läst?", "Visste du att…?", "Har du hört talas om …?",
    "Nähä!", "massmediet, massmedier, massmedierna)", "Vad har hänt?", "Vad tänker du på?",
    "Tänker ni…", "Tror du att…?", "förra veckan", "Vad tänker du göra när…?",
    "–Hej! Det var länge sedan!", "just det", "–Jo, det är bara bra.", "–Själv då?",
    "Jaha, då ska vi se …", "Det passar bra.", "för några dagar sedan", "i måndags",
    "senast på fredag", "nästan aldrig", "inte på flera månader", "flera gånger i veckan",
    "vartannat år", "i somras", "Jag vet inte riktigt.", "Det var hemskt trevligt.",
    "känd för att ha", "Ju … desto", "hela dagen", "för skojs skull", "en skam för …",
    "den här veckan", "Du kommer inte att tro dina öron!", "Vi får väl se.", "som vanligt",
    "Hur dum får man vara?", "råttan i pizzan", "Jo, det är sant!", "Jo, jag lovar!",
    "morgonen därpå", "lika stor som", "en tredjedel så stort som", "form av",
    "i längden", "inte se klok ut", "per dygn", "på det sättet",

    # Prepositional & Adverbial phrases
    "i centrum", "på första plats", "i allmänhet", "sedan dess", "i alla tider",
    "istället för", "strax utanför", "hemma hos", "inom parentes", "av olika slag",
    "en viss tid", "ingen annanstans", "strax innan", "på senare tid", "mot slutet av",
    "tack vare", "till en början", "vid kontakt med", "direkt efter", "i vintras",
    "under lång tid", "i knät", "meter över havet", "till ytan", "i princip",

    # Pure adverbs, prepositions, conjunctions, subjunctions, pronouns, English words
    "därmed", "dessutom", "verkligen", "äntligen", "även om", "genom att", "medan",
    "förresten", "inte…förrän", "fastän", "tills", "about", "sist", "jämt", "jo",
    "ifall", "förrän", "allihop", "nuförtiden", "med tiden", "alltså", "bör",
    "istället", "en", "nedan", "var och en", "var sin", "annars", "detsamma som",
    "i övermorgon", "efteråt", "book", "climate", "Sami", "fylle-"
}

