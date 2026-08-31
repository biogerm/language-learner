import json
import re

text = """När min granne frågade hur jag mådde sa jag: "–Jo, det är bara bra." Men sanningen är att den här veckan har varit ganska stressig. I måndags bestämde jag mig för en ny livsstil. Förra veckan bestämde jag mig för att förändra varje vardaglig rutin jag hade. Jag hade nämligen svåra sömnproblem. Min läkare gav mig ett val: antingen…eller. Han tyckte jag skulle vara ute mer utanför hemmet.

För några dagar sedan började jag promenera. Jag gick till en klädbutik som hade en stor realisation hela dagen. Istället för att titta i en gammal katalog köpte jag en ny vit baddräkt och en extra tjock strumpa. Men plötsligt märkte jag att min plånbok var borta. Jag ville inte råka göra något dumt eller verka som att jag försökte snatta. Jag tänkte fråga efter någon i personalen som kunde agera. De hittade den inte. Jag brukar inte snåla, men en dyr klocka jag hade i väskan var också borta. Hade jag lagt den någonstans? 

Morgonen därpå var det iskallt och marken var isig. Jag tog en ful jacka och ett paraply. Jag var inte van vid kylan och började frysa ända in i min själ. Jag tänkte drömma mig bort. Min nuvarande lägenhet är inte lika stor som huset jag bodde i när jag var 10 år gammal, men varje detalj är viktig. Jag gick in i mitt sovrum för att vila i en kvart. 

"Förbered dig för i övermorgon!" sa en sjungande röst i radion. Det var ett program om en duktig husmor. Ett tips var att städa ur sitt kylskåp, ett annat var att bada bastu i sitt lilla badrum för att ta det lugnt. Att bada bastu är en användbar metod för avkoppling. Jag har faktiskt inte badat bastu alls, i alla fall inte på flera månader. Förut badade jag flera gånger i veckan. 

Efter ett par dagar kände jag mig bättre. Jag slutade ge upp och bestämde mig för att släppa ut all stress. Om något går sönder, vad kommer det betyda om hundra år? Man måste sova åtta timmar per dygn, minst en viss tid för sig själv. Mitt favoritlag kom på sjunde plats i ligan, men vad gör det? Livet går vidare!"""

core_words = [
    "utanför hemmet", "10 år gammal", "förra veckan", "vardaglig", "råka", 
    "i övermorgon", "för några dagar sedan", "i måndags", "inte på flera månader", 
    "flera gånger i veckan", "klocka", "göra något dumt", "hela dagen", "realisation", 
    "plånbok", "den här veckan", "snatta", "morgonen därpå", "strumpa", "van vid", 
    "sovrum", "användbar", "per dygn", "sömnproblem", "ful", "husmor", "paraply", 
    "ett par dagar", "granne", "vara ute", "kvart", "bada bastu", "livsstil", 
    "ta det lugnt", "badrum", "kylskåp", "katalog", "baddräkt"
]

glue_words = [
    "antingen…eller", "sjunde plats", "sjungande", "detalj", "vit", 
    "inte lika stor", "betyda", "förbered", "verka", "en viss tid", 
    "fråga efter någon", "någonstans", "frysa", "snåla", "agera", "själ", 
    "drömma", "isig", "–Jo, det är bara bra.", "ge upp", "släppa ut", "sönder"
]

target_mappings = [
    # Core
    ("utanför hemmet", "utanför hemmet"),
    ("10 år gammal", "10 år gammal"),
    ("förra veckan", "Förra veckan"),
    ("vardaglig", "vardaglig"),
    ("råka", "råka"),
    ("i övermorgon", "i övermorgon"),
    ("för några dagar sedan", "För några dagar sedan"),
    ("i måndags", "I måndags"),
    ("inte på flera månader", "inte på flera månader"),
    ("flera gånger i veckan", "flera gånger i veckan"),
    ("klocka", "klocka"),
    ("göra något dumt", "göra något dumt"),
    ("hela dagen", "hela dagen"),
    ("realisation", "realisation"),
    ("plånbok", "plånbok"),
    ("den här veckan", "den här veckan"),
    ("snatta", "snatta"),
    ("morgonen därpå", "Morgonen därpå"),
    ("strumpa", "strumpa"),
    ("van vid", "van vid"),
    ("sovrum", "sovrum"),
    ("användbar", "användbar"),
    ("per dygn", "per dygn"),
    ("sömnproblem", "sömnproblem"),
    ("ful", "ful"),
    ("husmor", "husmor"),
    ("paraply", "paraply"),
    ("ett par dagar", "ett par dagar"),
    ("granne", "granne"),
    ("vara ute", "vara ute"),
    ("kvart", "kvart"),
    ("bada bastu", "bada bastu"),
    ("livsstil", "livsstil"),
    ("ta det lugnt", "ta det lugnt"),
    ("badrum", "badrum"),
    ("kylskåp", "kylskåp"),
    ("katalog", "katalog"),
    ("baddräkt", "baddräkt"),

    # Glue
    ("antingen…eller", "antingen…eller"),
    ("sjunde plats", "sjunde plats"),
    ("sjungande", "sjungande"),
    ("detalj", "detalj"),
    ("vit", "vit"),
    ("inte lika stor", "inte lika stor"),
    ("betyda", "betyda"),
    ("förbered", "Förbered"),
    ("verka", "verka"),
    ("en viss tid", "en viss tid"),
    ("fråga efter någon", "fråga efter någon"),
    ("någonstans", "någonstans"),
    ("frysa", "frysa"),
    ("snåla", "snåla"),
    ("agera", "agera"),
    ("själ", "själ"),
    ("drömma", "drömma"),
    ("isig", "isig"),
    ("–Jo, det är bara bra.", "–Jo, det är bara bra."),
    ("ge upp", "ge upp"),
    ("släppa ut", "släppa ut"),
    ("sönder", "sönder")
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
    "article_id": "art_31",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('course/sfid/phase2/article_31.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
