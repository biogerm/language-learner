import json
import re

text = """För en lång period bodde jag i en gammal lägenhet. På den tiden kände jag mig ofta ofräsch och smutsig för vi hade inget bra badrum. Jag brukade ligga vaken på natten. Jag kände mig nästan som ett trött skelett och tyckte att rummet försökte hålla i fångenskap min energi. Men jag har alltid varit intresserad av… ja, inredning och fastigheter. Så på senare tid började jag leta efter en ny bostad. Det blev början på en spännande tid.

Ett bra husköp brukar alltid ta tid och huspriser kan vara extrema. Varannan kväll brukade jag följa marknaden och skriva en lista över intressanta objekt. En viktig aspekt var att hemmet skulle passa min personlighet. "Jag hänger inte med riktigt!" sa min vän, för jag hade varit på visning en massa gånger. Till slut bestämde jag mig för att förhandla om en liten lyxvilla och köpa den med mina sparade pengar. Min gamla lägenhet skulle jag givetvis sälja. Huset jag köpte hade en vacker brun dörr. Jag köpte också en tavla med ett vackert nattmotiv som skulle få stå i centrum i mitt nya vardagsrum. 

Idag kan jag verkligen säga: Vi har det jättebra här i … vår lilla by. Mitt nya hushåll fungerar mycket bättre. Än idag njuter jag av mitt nya hem. Jag brukar gå upp klockan åtta varje morgon. Jag trycker på en knapp på kaffemaskinen. Det är viktigt att tvätta sig, raka sig och kamma sig innan man går ut. Ibland måste man också klippa sig för att förbli fin. Sedan sätter jag på mig en bekväm sko och är redo. "Bostad" är förresten ett bra samlingsnamn för en plats där man kan bo. 

Vad händer imorgon? Jo, på min fritid ska jag besöka ett vackert operahus och sedan ett stort badhus. Det fick jag i födelsedagspresent av en kompis. Nästa gång hoppas jag att vi kan komma in i en lugn stund och ha en rolig spelkväll. Kanske kommer någon konstnärlig kritiker på besök som är lik mig i smaken. Vid den här tiden njuter jag bara av livet."""

core_words = [
    "fritid", "på den tiden", "hushåll", "idag", "ta tid", "morgon", "kväll", 
    "jag har alltid varit intresserad av…", "sko", "Vad händer imorgon?", "bo", 
    "ofräsch", "raka sig", "kamma sig", "smutsig", "klippa sig", "tvätta sig", 
    "pengar", "en massa gånger", "nästa gång", "födelsedagspresent", "period", 
    "lägenhet", "spelkväll", "sälja", "än idag", "vid den här tiden", "bostad", 
    "operahus", "Vi har det jättebra här i …", "nattmotiv", "köpa", "badhus", 
    "husköp", "förhandla", "lyxvilla", "dörr", "huspris"
]

glue_words = [
    "på senare tid", "personlighet", "förbli", "extrem", "ligga vaken", 
    "hålla i fångenskap", "stund", "aspekt", "gammal", "brun", "åtta", "varannan", 
    "kritiker", "lik", "Jag hänger inte med riktigt!", "lista", "stå i centrum", 
    "knapp", "följa", "skelett", "samlingsnamn", "komma in i"
]

target_mappings = [
    # Core
    ("fritid", "fritid"),
    ("på den tiden", "På den tiden"),
    ("hushåll", "hushåll"),
    ("idag", "Idag"),
    ("ta tid", "ta tid"),
    ("morgon", "morgon"),
    ("kväll", "kväll"),
    ("jag har alltid varit intresserad av…", "jag har alltid varit intresserad av…"),
    ("sko", "sko"),
    ("Vad händer imorgon?", "Vad händer imorgon?"),
    ("bo", "bo"),
    ("ofräsch", "ofräsch"),
    ("raka sig", "raka sig"),
    ("kamma sig", "kamma sig"),
    ("smutsig", "smutsig"),
    ("klippa sig", "klippa sig"),
    ("tvätta sig", "tvätta sig"),
    ("pengar", "pengar"),
    ("en massa gånger", "en massa gånger"),
    ("nästa gång", "Nästa gång"),
    ("födelsedagspresent", "födelsedagspresent"),
    ("period", "period"),
    ("lägenhet", "lägenhet"),
    ("spelkväll", "spelkväll"),
    ("sälja", "sälja"),
    ("än idag", "Än idag"),
    ("vid den här tiden", "Vid den här tiden"),
    ("bostad", "bostad"),
    ("operahus", "operahus"),
    ("Vi har det jättebra här i …", "Vi har det jättebra här i …"),
    ("nattmotiv", "nattmotiv"),
    ("köpa", "köpa"),
    ("badhus", "badhus"),
    ("husköp", "husköp"),
    ("förhandla", "förhandla"),
    ("lyxvilla", "lyxvilla"),
    ("dörr", "dörr"),
    ("huspris", "huspriser"),

    # Glue
    ("på senare tid", "på senare tid"),
    ("personlighet", "personlighet"),
    ("förbli", "förbli"),
    ("extrem", "extrema"),
    ("ligga vaken", "ligga vaken"),
    ("hålla i fångenskap", "hålla i fångenskap"),
    ("stund", "stund"),
    ("aspekt", "aspekt"),
    ("gammal", "gammal"),
    ("brun", "brun"),
    ("åtta", "åtta"),
    ("varannan", "Varannan"),
    ("kritiker", "kritiker"),
    ("lik", "lik"),
    ("Jag hänger inte med riktigt!", "Jag hänger inte med riktigt!"),
    ("lista", "lista"),
    ("stå i centrum", "stå i centrum"),
    ("knapp", "knapp"),
    ("följa", "följa"),
    ("skelett", "skelett"),
    ("samlingsnamn", "samlingsnamn"),
    ("komma in i", "komma in i")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if base == "sko":
        start = text.find("bekväm sko") + 7
    elif base == "bo":
        start = text.find("man kan bo.") + 8
    elif base == "period":
        start = text.find("För en lång period") + 12
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
    "step_id": "vardagsliv",
    "step_title": "Vardagsliv",
    "article_id": "art_29",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('./course/sfid/phase2/article_29.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
