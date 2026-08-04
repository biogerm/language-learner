import json
import re

text = """"Hur ser det ut?" frågade min glada singelvän. Vi stod mitt i rummet och tittade ut över ett enormt stort arrangemang. Det var ganska länge sedan vi senast träffades. Han var min bästis, en otroligt stilig polare och en mycket nära vän ända sedan min ungdom. 

Han var ofta en riktig träningsnarkoman och ibland även en stressad arbetsnarkoman. Jag själv var mer som en vanlig, lugn person. Jag var nervös inför denna dag. Vi var inbjudna till en exklusiv fest för att fira min farfar och mormor. De hade totalt bjudit över hundra gäster. Både mina farföräldrar och morföräldrar tyckte mycket om att samla ihop alla små barnbarn, några trevliga bybor, lokal skolpersonal och även min äldre syster. Det kändes som ett genuint, varmt barndomsminne. Familjen var mycket känd i vårt lilla område, de var nästan som en rik gammal adelsfamilj.

"Jag minns särskilt när din farfar berättade sin långa, fascinerande släktkrönika," sa han. "Historien kunde vara rätt grym, ofta med någon elak person i centrum, men sagan hade alltid ett lyckligt slut. Det är en typ av berättelse man verkligen älskar."

Under den långa festen åt vi god kaka med mandel och lyssnade på glad musik från en lite repig cd-skiva. En inbjuden riksdagsman och en mycket stolt same höll vackra tal till hela vårt land, ungefär som en hyllning till Moder Svea. Det hela hade en jätteviktig och seriös funktion i just detta sammanhang. "Tror du det är okej om jag försöker blanda ihop dessa gäster lite?" frågade min vän skämtsamt, och jag såg att han uppenbarligen var förälskad i någon ny på festen. Han ville nämligen gärna dyka upp på helt rätt plats vid rätt tid. 

"Ja absolut, njut och skratta så mycket du kan," svarade jag. Jag ville ju inte alls hata kärleken. "Jag tycker att romantik är härligt. Man får inte vara oförstående inför den." 

"Det ryktas att vår granne vill gifta om sig," skämtade han sedan glatt. 

"Tror du att min gamla berättelse från föregående år kan stämma?" sa farfar plötsligt från ingenstans. Det var en mycket oväntad fråga från honom. 

"Vem vill inte krama och pussa på någon man verkligen tycker om?" log farfar. Han hade nyligen fått ett intressant förslag. Han ville underteckna ett viktigt papper om den gamla gården som låg vackert vid en stor korsning. Han älskade verkligen gården. "Här kan man ibland ligga ner på det mjuka gräset, titta upp och känna sig helt osynlig i världen. Jag gillar verkligen den här typen av … tysta och fridfulla platser."

"Hoppas att vi ses snart!" ropade alla de glada gästerna när de sedan var tvungna att återvända hemåt i den mörka, stjärnklara natten."""

core_words = [
    "singelvän", "sammanhang", "arbetsnarkoman", "träningsnarkoman", "bästis", 
    "mormor", "oväntad", "mandel", "arrangemang", "återvända", "adelsfamilj", 
    "barnbarn", "nära vän", "barndomsminne", "farföräldrar", "morföräldrar", 
    "polare", "farfar", "Moder Svea", "riksdagsman", "nervös", "skolpersonal", 
    "hata", "ungdom", "släktkrönika", "syster", "gifta om sig", "elak", 
    "lyckligt slut", "grym", "oförstående", "pussa på", "same", "förälskad", 
    "ligga", "den här typen av …", "blanda ihop", "en typ av"
]

glue_words = [
    "jätteviktig", "föregående", "hundra", "stilig", "exklusiv", "korsning", 
    "vanlig", "mitt i", "Hur ser det ut?", "så mycket du kan", "stämma", 
    "dessa", "funktion", "cd-skiva", "plats", "dyka upp", "gärna", 
    "Hoppas att vi ses snart!", "osynlig", "underteckna", "länge sedan", "förslag"
]

target_mappings = [
    # Core
    ("singelvän", "singelvän"),
    ("sammanhang", "sammanhang"),
    ("arbetsnarkoman", "arbetsnarkoman"),
    ("träningsnarkoman", "träningsnarkoman"),
    ("bästis", "bästis"),
    ("mormor", "mormor"),
    ("oväntad", "oväntad"),
    ("mandel", "mandel"),
    ("arrangemang", "arrangemang"),
    ("återvända", "återvända"),
    ("adelsfamilj", "adelsfamilj"),
    ("barnbarn", "barnbarn"),
    ("nära vän", "nära vän"),
    ("barndomsminne", "barndomsminne"),
    ("farföräldrar", "farföräldrar"),
    ("morföräldrar", "morföräldrar"),
    ("polare", "polare"),
    ("farfar", "farfar"),
    ("Moder Svea", "Moder Svea"),
    ("riksdagsman", "riksdagsman"),
    ("nervös", "nervös"),
    ("skolpersonal", "skolpersonal"),
    ("hata", "hata"),
    ("ungdom", "ungdom"),
    ("släktkrönika", "släktkrönika"),
    ("syster", "syster"),
    ("gifta om sig", "gifta om sig"),
    ("elak", "elak"),
    ("lyckligt slut", "lyckligt slut"),
    ("grym", "grym"),
    ("oförstående", "oförstående"),
    ("pussa på", "pussa på"),
    ("same", "same"),
    ("förälskad", "förälskad"),
    ("ligga", "ligga"),
    ("den här typen av …", "den här typen av …"),
    ("blanda ihop", "blanda ihop"),
    ("en typ av", "en typ av"),

    # Glue
    ("jätteviktig", "jätteviktig"),
    ("föregående", "föregående"),
    ("hundra", "hundra"),
    ("stilig", "stilig"),
    ("exklusiv", "exklusiv"),
    ("korsning", "korsning"),
    ("vanlig", "vanlig"),
    ("mitt i", "mitt i"),
    ("Hur ser det ut?", "Hur ser det ut?"),
    ("så mycket du kan", "så mycket du kan"),
    ("stämma", "stämma"),
    ("dessa", "dessa"),
    ("funktion", "funktion"),
    ("cd-skiva", "cd-skiva"),
    ("plats", "plats"),
    ("dyka upp", "dyka upp"),
    ("gärna", "gärna"),
    ("Hoppas att vi ses snart!", "Hoppas att vi ses snart!"),
    ("osynlig", "osynlig"),
    ("underteckna", "underteckna"),
    ("länge sedan", "länge sedan"),
    ("förslag", "förslag")
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
    "step_id": "relationer_känslor",
    "step_title": "Relationer & Känslor",
    "article_id": "art_51",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('./course/sfid/phase2/article_51.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
