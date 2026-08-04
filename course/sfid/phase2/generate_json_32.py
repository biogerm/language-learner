import json
import re

text = """"Vet du vem som frågade efter dig?" sa min vän. Det var en sällskapsdam från förr. Hon var väldigt fattig i början, men nu jobbade hon på ett exklusivt hunddagis här i vår lilla förort. Jag var trött och tyckte att det är skönt att lata sig och vara en riktig soffpotatis. Men denna morgon blev en rivstart. Det är så lätt att försova sig när man är trött, och jag vaknade jättesent. "jag skulle vilja…" tänkte jag, "bara ligga kvar under täcket". Jag var tvungen att skynda. Jag fick snabbt ta på mig kläderna och skynda på rejält för att hinna.

Egentligen gillar jag inredning. Jag ville stanna hemma och bygga en balkong för att ordna en skön plats att sitta på. Men nu hade jag bråttom. Jag la min utrustning i en stor påse. Jag tog med badbyxor och simglasögon. Trots min ålder kände jag mig stark som en oxe. Jag ville inte stanna inne och suga åt mig negativ energi, så jag bestämde mig för att flytta ut på stan. 

Det var verkligen en hektisk dag. Mycket folk var ute. Jag gick till simhallen som hade en gemensam bastu. Simhallen var uppdelad i olika sektioner av en storlek som var enorm. Jag ville klättra upp för det höga hopptornet. Efter badet fick man torka sig själv noggrant.

Jag funderade på att ringa till frisören för en klippning i en snygg salong, så jag skulle slippa se tråkig ut. Jag upptäckte också att jag hade ett litet hål i min tröja. Jag tänkte på att boka en traditionell husmorssemester, men det var ett högt tryck på alla biljetter. Varje siffra i prislistan var otroligt hög, och jag kände mig pyttelite orolig. "Vad vill du syssla med?" frågade min vän, som var likadan som jag. Vi verkade höra ihop genom starka kulturella band. Det är viktigt att höra av sig till gamla vänner. 

Plötsligt försökte någon typ av vild hund, som nog kanske var dräktig, angripa en soptunna på gatan. Jag tänkte att jag hade fått en intressant erfarenhet idag. Klockan fyra var det dags att gå hem och lägga sig."""

core_words = [
    "balkong", "klockan fyra", "bastu", "syssla med", "lata sig", "inredning", 
    "folk", "skynda", "hål", "påse", "simglasögon", "slippa", "ringa till", 
    "badbyxor", "ta på", "ordna", "bygga", "soffpotatis", "lägga sig", "skön", 
    "skynda på", "rivstart", "snygg", "ålder", "utrustning", "flytta", 
    "husmorssemester", "salong", "höra av sig", "hunddagis", "sällskapsdam", 
    "klippning", "siffra", "pyttelite", "förort", "torka sig", "själv", "försova sig"
]

glue_words = [
    "vild", "stark som en oxe", "suga", "Vet du vem som frågade efter dig?", 
    "fattig", "här", "i början", "erfarenhet", "klättra", "hektisk", "högt tryck", 
    "angripa", "uppdelad", "gemensam", "likadan", "höra ihop", "kulturella band", 
    "någon typ av", "storlek", "jag skulle vilja…", "nog", "dräktig"
]

target_mappings = [
    # Core
    ("balkong", "balkong"),
    ("klockan fyra", "Klockan fyra"),
    ("bastu", "bastu"),
    ("syssla med", "syssla med"),
    ("lata sig", "lata sig"),
    ("inredning", "inredning"),
    ("folk", "folk"),
    ("skynda", "skynda"),
    ("hål", "hål"),
    ("påse", "påse"),
    ("simglasögon", "simglasögon"),
    ("slippa", "slippa"),
    ("ringa till", "ringa till"),
    ("badbyxor", "badbyxor"),
    ("ta på", "ta på"),
    ("ordna", "ordna"),
    ("bygga", "bygga"),
    ("soffpotatis", "soffpotatis"),
    ("lägga sig", "lägga sig"),
    ("skön", "skön"),
    ("skynda på", "skynda på"),
    ("rivstart", "rivstart"),
    ("snygg", "snygg"),
    ("ålder", "ålder"),
    ("utrustning", "utrustning"),
    ("flytta", "flytta"),
    ("husmorssemester", "husmorssemester"),
    ("salong", "salong"),
    ("höra av sig", "höra av sig"),
    ("hunddagis", "hunddagis"),
    ("sällskapsdam", "sällskapsdam"),
    ("klippning", "klippning"),
    ("siffra", "siffra"),
    ("pyttelite", "pyttelite"),
    ("förort", "förort"),
    ("torka sig", "torka sig"),
    ("själv", "själv"),
    ("försova sig", "försova sig"),

    # Glue
    ("vild", "vild"),
    ("stark som en oxe", "stark som en oxe"),
    ("suga", "suga"),
    ("Vet du vem som frågade efter dig?", "Vet du vem som frågade efter dig?"),
    ("fattig", "fattig"),
    ("här", "här"),
    ("i början", "i början"),
    ("erfarenhet", "erfarenhet"),
    ("klättra", "klättra"),
    ("hektisk", "hektisk"),
    ("högt tryck", "högt tryck"),
    ("angripa", "angripa"),
    ("uppdelad", "uppdelad"),
    ("gemensam", "gemensam"),
    ("likadan", "likadan"),
    ("höra ihop", "höra ihop"),
    ("kulturella band", "kulturella band"),
    ("någon typ av", "någon typ av"),
    ("storlek", "storlek"),
    ("jag skulle vilja…", "jag skulle vilja…"),
    ("nog", "nog"),
    ("dräktig", "dräktig")
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
    "step_id": "vardagsliv",
    "step_title": "Vardagsliv",
    "article_id": "art_32",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('./course/sfid/phase2/article_32.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
