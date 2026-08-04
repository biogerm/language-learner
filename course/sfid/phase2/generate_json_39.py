import json
import re

text = """Att ha ett roligt intresse kan visa sig på olika sätt. Vissa älskar litteratur, vilket är ett vackert uttryck för tankar. De kanske vill ställa ut en fin bild på ett museum. Andra vill sticka iväg och leta efter ett ovanligt frimärke. Kanske de vill skapa en dialog om kultur. Men för mig är idrott det viktigaste i min värld. 
"Jag älskar att springa. –Själv då?" frågade en vän mig en kall höst. "Vad gillar du för aktivitet?"

Jag gillar löpning och lätt joggning. Ibland brukar jag springa ett långt lopp, som till exempel ett ultramaraton. Men det finns annat jag gör. Jag gillar cykling och orientering i skogen, där mitt skarpa luktsinne får njuta av frisk luft. När jag var på ett sommarläger förra året fick jag pröva rolig segling och tuff surfning. Vi fick även bada och öva på simning mycket i sjön. Ibland spelade vi volleyboll vid stranden, och handboll eller fotboll på gräset. Vi testade även basket. Allt detta har en positiv effekt på mig, och ingen sport är skadlig om man är försiktig. Man måste helt enkelt välkomna alla chanser till lek. 

Vintertid byter jag sporter. Jag åker mycket längdskidåkning och tar fram mina bästa skidor. Det är också kul med snowboardåkning, men man måste alltid ha en hjälm för att skydda huvudet. Jag gillar också ishockey. Man slår pucken i ett nät med en klubba för att få poäng och vinna. "Det skulle vara bättre att… inte attackera varandra så hårt på isen," brukar jag skoja. 

Man har idrottat sedan år 1 e.kr. Efter Kristus, och jag är glad för mitt val av livsstil. Jag kan ha hand om min egen träning och halvera min stressnivå. Ibland lyfter jag en skivstång på gymmet, eller gör lite intensiv gympa med bra taktkänsla. Det går också jättebra att spela bordtennis eller gå ut på en lång promenad med stavgång. Till och med e-sport eller ett spännande lajv kan locka mig, om jag vill stanna inne. Ibland måste jag boka och beställa tid för vila, men jag gör allt i ett och samma liv!"""

core_words = [
    "litteratur", "bada", "surfning", "uttryck", "längdskidåkning", 
    "skivstång", "ishockey", "klubba", "poäng", "volleyboll", "e-sport", 
    "idrott", "löpning", "ultramaraton", "stavgång", "gympa", "orientering", 
    "intresse", "basket", "bild", "fotboll", "handboll", "sommarläger", 
    "lajv", "joggning", "bordtennis", "frimärke", "nät", "simning", "segling", 
    "aktivitet", "dialog", "lopp", "cykling", "snowboardåkning", "taktkänsla", 
    "hjälm", "skidor", "ställa ut"
]

glue_words = [
    "visa sig", "öva", "annat", "luktsinne", "värld", "på olika sätt", 
    "Det skulle vara bättre att…", "attackera", "halvera", "vintertid", 
    "effekt", "–Själv då?", "skadlig", "ett och samma", "välkomna", 
    "e.kr. Efter Kristus", "val", "höst", "beställa tid", "sticka iväg", 
    "ha hand om"
]

target_mappings = [
    # Core
    ("litteratur", "litteratur"),
    ("bada", "bada"),
    ("surfning", "surfning"),
    ("uttryck", "uttryck"),
    ("längdskidåkning", "längdskidåkning"),
    ("skivstång", "skivstång"),
    ("ishockey", "ishockey"),
    ("klubba", "klubba"),
    ("poäng", "poäng"),
    ("volleyboll", "volleyboll"),
    ("e-sport", "e-sport"),
    ("idrott", "idrott"),
    ("löpning", "löpning"),
    ("ultramaraton", "ultramaraton"),
    ("stavgång", "stavgång"),
    ("gympa", "gympa"),
    ("orientering", "orientering"),
    ("intresse", "intresse"),
    ("basket", "basket"),
    ("bild", "bild"),
    ("fotboll", "fotboll"),
    ("handboll", "handboll"),
    ("sommarläger", "sommarläger"),
    ("lajv", "lajv"),
    ("joggning", "joggning"),
    ("bordtennis", "bordtennis"),
    ("frimärke", "frimärke"),
    ("nät", "nät"),
    ("simning", "simning"),
    ("segling", "segling"),
    ("aktivitet", "aktivitet"),
    ("dialog", "dialog"),
    ("lopp", "lopp"),
    ("cykling", "cykling"),
    ("snowboardåkning", "snowboardåkning"),
    ("taktkänsla", "taktkänsla"),
    ("hjälm", "hjälm"),
    ("skidor", "skidor"),
    ("ställa ut", "ställa ut"),

    # Glue
    ("visa sig", "visa sig"),
    ("öva", "öva"),
    ("annat", "annat"),
    ("luktsinne", "luktsinne"),
    ("värld", "värld"),
    ("på olika sätt", "på olika sätt"),
    ("Det skulle vara bättre att…", "Det skulle vara bättre att…"),
    ("attackera", "attackera"),
    ("halvera", "halvera"),
    ("vintertid", "Vintertid"),
    ("effekt", "effekt"),
    ("–Själv då?", "–Själv då?"),
    ("skadlig", "skadlig"),
    ("ett och samma", "ett och samma"),
    ("välkomna", "välkomna"),
    ("e.kr. Efter Kristus", "e.kr. Efter Kristus"),
    ("val", "val"),
    ("höst", "höst"),
    ("beställa tid", "beställa tid"),
    ("sticka iväg", "sticka iväg"),
    ("ha hand om", "ha hand om")
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
    "step_id": "kultur_nöje",
    "step_title": "Kultur & Nöje",
    "article_id": "art_39",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('./course/sfid/phase2/article_39.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
