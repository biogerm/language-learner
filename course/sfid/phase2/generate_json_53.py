import json
import re

text = """Hej … Anna!
Hur är läget? Nu är vi framme i … vår fina gamla stad, och jag mår jättebra. Jag måste berätta något … väldigt otroligt som precis hände. 

Herregud, du kommer inte att tro det! En gammal nordisk släkting till mig dök plötsligt upp här. Han är känd för att vara väldigt händig och pålitlig, en genuint ordentlig man. Många brukar anse att han är enormt förmögen och rik. "Du skojar!" sa jag när han var spontan och kom hit. Han sa stolt att hans senaste utveckling på jobbet var en stor succé, mycket tack vare hans envishet. 

Han är oftast utåtriktad och pratsam, men verkade lite orolig. Han avslöjade i hemlighet att han tyckte att jag var för slarvig och kanske även ganska lat. Det var en hemsk och rentav taskig sak att säga. Han var oartig och fällde faktiskt en jättedum kommentar. Jag ville verkligen inte vara falsk, så jag blev upprörd och inte alls nöjd. Man måste kunna koncentrera sig för att alltid vara snäll. 

Han ville be att få mer kaffe, och passade också på att be om min hjälp för att söka ett stort jobb i en bred skala åt en vän. Han brukade ofta sätta i system att utnyttja folks godhet. Jag tyckte att hans beteende var detsamma som att vara egoistisk. Förr i tiden diskuterade man ofta tydlig könsroll och utlänningar pratade om ”Den svenska synden”, men i dagens samhälle kräver all sann framgång att man har en bra inre egenskap som ett stort tålamod. Det är viktigt att vara harmonisk för att ens drömmar ska kunna bli verklighet. 

Till slut kunde vi ändå komma fram till en bra lösning. Han bad om ursäkt och jag lovade att besvara hans frågor för att få slut på konflikten. Vi diskuterade hans nyhet och några små problem. Jag började berätta om mina planer. Det brukar ju heta att ju mer …desto bättre, och vi pratade länge. Vi väntade tills stormen var över. Sedan stack han iväg snabbt som ett skott. 

Jag är trots allt glad och väldigt tacksam över att vi har en mycket mer meningsfull relation, du och jag. Jag kan rekommendera att du reser hit snart. En varm hälsning till dig!
Längtar efter dig!"""

core_words = [
    "falsk", "egenskap", "Herregud", "ordentlig", "tacksam", "hälsning", 
    "lat", "envishet", "jag", "tålamod", "nöjd", "harmonisk", "berätta", 
    "slarvig", "orolig", "meningsfull", "pratsam", "snäll", "be att få", 
    "Hur är läget?", "be om", "i hemlighet", "Hej …", "spontan", "jättedum", 
    "Nu är vi framme i …", "könsroll", "oartig", "hemsk", "nyhet", "pålitlig", 
    "taskig", "Längtar efter dig!", "framgång", "Jag måste berätta något …", 
    "utåtriktad", "händig", "släkting"
]

glue_words = [
    "små", "detsamma som", "succé", "koncentrera sig", "sätta i", "anse", 
    "besvara", "tack vare", "nordisk", "Du skojar!", "förmögen", "skott", 
    "utveckling", "tills", "söka", "rekommendera", "ju mer …desto", 
    "för att få", "komma fram", "skala", "bli verklighet", "”Den svenska synden”"
]

target_mappings = [
    # Core
    ("falsk", "falsk"),
    ("egenskap", "egenskap"),
    ("Herregud", "Herregud"),
    ("ordentlig", "ordentlig"),
    ("tacksam", "tacksam"),
    ("hälsning", "hälsning"),
    ("lat", "lat"),
    ("envishet", "envishet"),
    ("jag", "jag"),
    ("tålamod", "tålamod"),
    ("nöjd", "nöjd"),
    ("harmonisk", "harmonisk"),
    ("berätta", "berätta"),
    ("slarvig", "slarvig"),
    ("orolig", "orolig"),
    ("meningsfull", "meningsfull"),
    ("pratsam", "pratsam"),
    ("snäll", "snäll"),
    ("be att få", "be att få"),
    ("Hur är läget?", "Hur är läget?"),
    ("be om", "be om"),
    ("i hemlighet", "i hemlighet"),
    ("Hej …", "Hej …"),
    ("spontan", "spontan"),
    ("jättedum", "jättedum"),
    ("Nu är vi framme i …", "Nu är vi framme i …"),
    ("könsroll", "könsroll"),
    ("oartig", "oartig"),
    ("hemsk", "hemsk"),
    ("nyhet", "nyhet"),
    ("pålitlig", "pålitlig"),
    ("taskig", "taskig"),
    ("Längtar efter dig!", "Längtar efter dig!"),
    ("framgång", "framgång"),
    ("Jag måste berätta något …", "Jag måste berätta något …"),
    ("utåtriktad", "utåtriktad"),
    ("händig", "händig"),
    ("släkting", "släkting"),

    # Glue
    ("små", "små"),
    ("detsamma som", "detsamma som"),
    ("succé", "succé"),
    ("koncentrera sig", "koncentrera sig"),
    ("sätta i", "sätta i"),
    ("anse", "anse"),
    ("besvara", "besvara"),
    ("tack vare", "tack vare"),
    ("nordisk", "nordisk"),
    ("Du skojar!", "Du skojar!"),
    ("förmögen", "förmögen"),
    ("skott", "skott"),
    ("utveckling", "utveckling"),
    ("tills", "tills"),
    ("söka", "söka"),
    ("rekommendera", "rekommendera"),
    ("ju mer …desto", "ju mer …desto"),
    ("för att få", "för att få"),
    ("komma fram", "komma fram"),
    ("skala", "skala"),
    ("bli verklighet", "bli verklighet"),
    ("”Den svenska synden”", "”Den svenska synden”")
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
    "article_id": "art_53",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('./course/sfid/phase2/article_53.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
