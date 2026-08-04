import json
import re

text = """Jag mötte min vän Sami på ett stort torg i staden. Han var trettiotre år gammal och hade precis flyttat till Sverige för att bosätta sig här. 
"Kan du prata lite långsammare?" bad han vänligt. "Jag vill förstå bättre och lära mig mer."

Vi diskuterade landets framtid och historia. Sami berättade: "Under 1800-talet och början av 1900-talet levde många européer i en stark monarki eller i ett mäktigt kejsardöme som var styrt av en grym kejsare. Vissa invånare tvingades konvertera till en specifik tro, till exempel bli lutherskt kristen, annars uppstod snabbt hot och stor otrygghet." 

"Ja, verkligen," sa jag. "Och i en ren diktatur var det mycket våld. Om en radikal socialistisk eller nationalistisk ledare ville förändra landet för snabbt, kunde ett farligt krig starta. Till och med i vårt fredliga land regleras makten i en lag som kallas successionsordningen. Många unga engagerar sig idag i ett ungdomsförbund för att kämpa för jämlikhet och regionalt självstyre."

Sami nickade förstående. "Vad gör du helst?" frågade han nyfiket. 
"Jag tycker att det är skönt att ibland vara för sig själv ute på en tyst brygga, men jag gillar också en bra politisk debatt," svarade jag. "Mycket politik handlar just nu om en ökad global import och hur vi kan exportera säkert till USA, hitta en tysk allians, eller undersöka en thailändsk marknad. Detta kräver en enormt bra samhällsplanering. Som man säger på engelska, det handlar about ekonomi."

"Va?! Du skojar!" utbrast Sami och skrattade. "Det låter väldigt komplicerat. Jag trodde att bara dyr mat skulle stå på menyn idag." 

Plötsligt hörde vi ett skrik. En kriminell tjuv hade försökt råna en butik i närheten och sedan försökt rymma. I paniken uppstod kaos i all lokal trafik. Två bilar, varav ett fordon tillhörde svensk militär, råkade krocka, vilket orsakade en allvarlig trafikolycka. Vi såg en chockerande olycka hända framför våra ögon. En högt uppsatt polisintendent kom dit för att försöka hantera situationen. Det var svårt att veta vem som är vem bland alla skrikande vittnen. 
Någon hävdade att en man blivit mördad av en känd mördare och sedan blivit skjuten, och att det funnits stor fiendskap dem emellan. Detta visade sig dock vara en ren osanning. Polisen grep tre stycken misstänkta personer på platsen, och valde att genast bjuda in alla inblandade till polisstationen för förhör."""

core_words = [
    "våld", "trafik", "krocka", "polisintendent", "exportera", "USA", 
    "otrygghet", "diktatur", "olycka", "råna", "trafikolycka", "allians", 
    "konvertera", "samhällsplanering", "militär", "rymma", "1900-talet", 
    "nationalistisk", "debatt", "tysk", "jämlikhet", "mördad", 
    "socialistisk", "thailändsk", "lutherskt kristen", "självstyre", 
    "ungdomsförbund", "1800-talet", "mördare", "import", "kriminell", 
    "torg", "krig", "monarki", "tjuv", "kejsardöme", "kejsare", "hot", 
    "successionsordningen", "Sami"
]

glue_words = [
    "brygga", "trettiotre", "framtid", "Va?! Du skojar!", "bosätta sig", 
    "emellan", "försöka", "vara för sig själv", "stycken", "about", 
    "stå på menyn", "Vad gör du helst?", "förändra", "mer", "bjuda in", 
    "dyr", "skjuten", "osanning", "vem som är vem", "Kan du prata lite långsammare?"
]

target_mappings = [
    # Core
    ("våld", "våld"),
    ("trafik", "trafik"),
    ("krocka", "krocka"),
    ("polisintendent", "polisintendent"),
    ("exportera", "exportera"),
    ("USA", "USA"),
    ("otrygghet", "otrygghet"),
    ("diktatur", "diktatur"),
    ("olycka", "olycka"),
    ("råna", "råna"),
    ("trafikolycka", "trafikolycka"),
    ("allians", "allians"),
    ("konvertera", "konvertera"),
    ("samhällsplanering", "samhällsplanering"),
    ("militär", "militär"),
    ("rymma", "rymma"),
    ("1900-talet", "1900-talet"),
    ("nationalistisk", "nationalistisk"),
    ("debatt", "debatt"),
    ("tysk", "tysk"),
    ("jämlikhet", "jämlikhet"),
    ("mördad", "mördad"),
    ("socialistisk", "socialistisk"),
    ("thailändsk", "thailändsk"),
    ("lutherskt kristen", "lutherskt kristen"),
    ("självstyre", "självstyre"),
    ("ungdomsförbund", "ungdomsförbund"),
    ("1800-talet", "1800-talet"),
    ("mördare", "mördare"),
    ("import", "import"),
    ("kriminell", "kriminell"),
    ("torg", "torg"),
    ("krig", "krig"),
    ("monarki", "monarki"),
    ("tjuv", "tjuv"),
    ("kejsardöme", "kejsardöme"),
    ("kejsare", "kejsare"),
    ("hot", "hot"),
    ("successionsordningen", "successionsordningen"),
    ("Sami", "Sami"),

    # Glue
    ("brygga", "brygga"),
    ("trettiotre", "trettiotre"),
    ("framtid", "framtid"),
    ("Va?! Du skojar!", "Va?! Du skojar!"),
    ("bosätta sig", "bosätta sig"),
    ("emellan", "emellan"),
    ("försöka", "försöka"),
    ("vara för sig själv", "vara för sig själv"),
    ("stycken", "stycken"),
    ("about", "about"),
    ("stå på menyn", "stå på menyn"),
    ("Vad gör du helst?", "Vad gör du helst?"),
    ("förändra", "förändra"),
    ("mer", "mer"),
    ("bjuda in", "bjuda in"),
    ("dyr", "dyr"),
    ("skjuten", "skjuten"),
    ("osanning", "osanning"),
    ("vem som är vem", "vem som är vem"),
    ("Kan du prata lite långsammare?", "Kan du prata lite långsammare?")
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
    "step_id": "samhälle_politik",
    "step_title": "Samhälle & Politik",
    "article_id": "art_47",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('./course/sfid/phase2/article_47.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
