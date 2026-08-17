import json
import re

with open("./course/sfid/phase1/master_dictionary.json", "r") as f:
    master = json.load(f)["words"]

with open("./course/sfid/phase3/data/chunks/keys_2.json", "r") as f:
    keys = json.load(f)

# Explicit manual classification overrides for edge cases in keys_2.json

# 1. EXPLICITLY REJECT (Not a Noun, Verb, or Adjective):
REJECT_EXPLICIT = {
    # Full sentences, questions, dialogue lines, exclamations with punctuation
    "Brukar du mysa?", "varifrån?", "faktum är att", "Visst låter det kul?", "puss puss",
    "inte…förrän", "Vet du när bussarna går?", "Vet du om?", "Jag skulle vilja veta hur…",
    "Vet du inte varför…?", "Vem frågade efter dig?", "Vad hände igår?", "Vad gjorde jag igår?",
    "Vet du vem som frågade efter dig?", "about", "Vet du vad jag gjorde igår…?",
    "Jag har ingen aning om…", "Ska vi ta en fika?", "Jag kan tyvärr inte idag.", "Läget?",
    "Jo, det är helt okej.", "Du då?", "Det är fint?", "Kom igen!", "Jag har inte ett öre.",
    "Det ordnar sig.", "en annan gång", "Okej då.", "Har du lust att…?", "Vad sägs om att…?",
    "Ska vi…?", "Tjaaa… jag vet inte rikitigt.", "Vet du vad som hände igår?",
    "Istället för att…", "Hur kommer det sig att…?", "”en sån” = vardagligt för en sådan",
    "mer eller mindre", "med tiden", "mot slutet av", "tack vare", "under senare delen av…",
    "till en början", "f.kr. Före Kristus", "e.kr. Efter Kristus", "10 år gammal",
    "Det är inte sant!", "Va?! Du skojar!", "Helt otroligt!", "Det hade jag ingen aning om.",
    "fram till år…", "historiskt sett", "vid kontakt med", "så… som möjligt", "Det sägs att…",
    "överdriv!", "Har du hört vad XX gjort?", "Vet du vad jag har läst?", "Visste du att…?",
    "Har du hört talas om …?", "Nähä!", "massmediet, massmedier, massmedierna)", "direkt efter",
    "Vad har hänt?", "Vad tänker du på?", "Tänker ni…", "Tror du att…?", "förra veckan",
    "Vad tänker du göra när…?", "se upp!", "–Hej! Det var länge sedan!", "just det",
    "–Jo, det är bara bra.", "–Själv då?", "inte längre", "i vintras", "Jaha, då ska vi se …",
    "i övermorgon", "Det passar bra.", "för några dagar sedan", "i måndags", "senast på fredag",
    "nästan aldrig", "inte på flera månader", "flera gånger i veckan", "vartannat år",
    "i somras", "Jag vet inte riktigt.", "Det var hemskt trevligt.", "känd för att ha",
    "Ju … desto", "hela dagen", "för skojs skull", "en skam för …", "den här veckan",
    "Du kommer inte att tro dina öron!", "Vi får väl se.", "som vanligt",
    "Hur dum får man vara?", "råttan i pizzan", "Jo, det är sant!", "Jo, jag lovar!",
    "morgonen därpå", "en", "i knät", "meter över havet", "till ytan", "lika stor som",
    "en tredjedel så stort som", "form av", "i längden", "inte se klok ut", "i princip",
    "per dygn", "på det sättet", "göra som man vill", "närma sig med stora steg",
    "book", "climate", "Sami", "fylle-", "Filmen handlar om…", "Filmen utspelar sig i",
    "Filmen bygger på en bok av…", "Filmen bygger på en verklig händelse.", "I slutet…",
    "”Det sjunde inseglet”", "”Fanny och Alexander”", "”Sommaren med Monica”",
    "”Den svenska synden”", "ett parti schack", "göra en paus", "vem som är vem",
    "precis som", "kallas för", "ta ett dopp", "titta in", "för länge sedan",
    "fler och fler", "få lust", "salta bad", "på order av", "sten efter sten",
    "tvåkilos", "ena", "fungera som", "även kallad", "guidad tur", "året runt",
    "ta sig runt", "till fots", "lugn och ro", "… för sig", "variant av", "en anledning till",
    "den här typen av …", "gjord av", "riven", "fylld med", "tärnad", "mitt itu",
    "stora delar av", "övrig", "något helt annat", "bakad på", "ugnsgräddad", "vispad",
    "en typ av", "långt in på nätterna", "en mängd", "femtio", "naturlig storlek",
    "komma ifrån", "pricka in", "någon gång", "Har du ätit det någon gång?",
    "Nej, det har jag aldrig gjort!", "Det låter hemskt!", "lika lön för lika arbete",
    "rätt till", "godkänd", "äg rum", "av olika slag", "en viss tid", "att göra något dumt"
}

# 2. EXPLICITLY ACCEPT (Is a Noun, Verb, or Adjective):
# Any valid Noun, Verb (including particle verbs like bidra till, bosätta sig, etc.), or Adjective (including participles like fryst, dräktig, etc.)

