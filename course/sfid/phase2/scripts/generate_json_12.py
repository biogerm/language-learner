import json
import re

text = """Jag älskar mat. I många år har jag tyckt om att baka och laga goda rätter. Min vän, som är en känd dramatiker, älskar mycket dramatik i köket. Efter att ha jobbat hela dagen var han hungrig som en varg. Han brukar säga att han gillar att äta som en häst när magen är tom. Jag tänkte föreslå att vi kunde gå ut och äta.

För en stund tänkte jag att vi skulle köpa hämtmat. Men hallen var trång och jag kände mig ntally trött efter jobbet. Vi valde att stanna hemma. Istället för att… gå på restaurang, började vi laga lättlagad plockmat och skära upp varje grönsak samt frukt som äpple och banan. "Det är inte sant!" ropade min vän plötsligt. En blodtörstig mygga hade gett honom ett getingstick. "En kommentar till," sa han, "och jag dör. Jag känner mig obekväm och behöver mer kolhydrat. Jag vill inte vara kritisk, men jag måste äta."

Jag bad honom att provsmaka lite salamikorv. "Du måste äta ordentligt för att inte sakna föda," sa jag. För att slippa ett misslyckande serverade jag rätten på en hög nivå. Doften av vitlök började sprida sig. Var och en fick en tallrik.

Vi ville dricka något gott. Jag drack kall läsk medan han tog en ljus öl. Ibland blandar han en drink, kanske en stor paraplydrink, men nu drack vi utan mycket socker. Vatten är annars bäst, för dricker man havsvatten blir man bara törstigare. Jag kunde vara säker på att min vän var nöjd. 

Efter middagen undrade jag: "Ska vi ta en fika?" Jag ville hellre baka en kaka än att äta köpt godis eller smågodis. Vi hade choklad hemma. Min vän ville dock bara ha en skål med lättyoghurt. Han tyckte att min mat för dagen var lite för dramatisk. Vi talade om att odla bär och hur man brukade sylta och safta förr i tiden, eller liknande saker. Jag hoppas vi kan ses nästnästa vecka igen, innan all glädje hinner försvinna."""

core_words = [
    "öl", "läsk", "dricka", "drink", "paraplydrink", "mat", "choklad", "banan", 
    "kolhydrat", "kaka", "lättyoghurt", "grönsak", "odla", "baka", "sylta", "safta", 
    "salamikorv", "gå ut och äta", "havsvatten", "törstigare", "restaurang", 
    "mat för dagen", "dramatisk", "hungrig som en varg", "att äta som en häst", 
    "föda", "dramatik", "dramatiker", "provsmaka", "blodtörstig", "lättlagad", 
    "plockmat", "hämtmat", "godis", "smågodis", "äpple", "socker", "Ska vi ta en fika?"
]

glue_words = [
    "för en stund", "nivå", "tom", "hellre … än", "trång", "nästnästa", "försvinna", 
    "ntally", "Det är inte sant!", "obekväm", "getingstick", "Istället för att…", 
    "kritisk", "sprida sig", "vara säker på", "misslyckande", "var och en", 
    "kommentar", "sakna", "år", "efter att ha", "liknande"
]

target_mappings = [
    # Core
    ("öl", "öl"),
    ("läsk", "läsk"),
    ("dricka", "dricka"),
    ("drink", "drink"),
    ("paraplydrink", "paraplydrink"),
    ("mat", "mat"),
    ("choklad", "choklad"),
    ("banan", "banan"),
    ("kolhydrat", "kolhydrat"),
    ("kaka", "kaka"),
    ("lättyoghurt", "lättyoghurt"),
    ("grönsak", "grönsak"),
    ("odla", "odla"),
    ("baka", "baka"),
    ("sylta", "sylta"),
    ("safta", "safta"),
    ("salamikorv", "salamikorv"),
    ("gå ut och äta", "gå ut och äta"),
    ("havsvatten", "havsvatten"),
    ("törstigare", "törstigare"),
    ("restaurang", "restaurang"),
    ("mat för dagen", "mat för dagen"),
    ("dramatisk", "dramatisk"),
    ("hungrig som en varg", "hungrig som en varg"),
    ("att äta som en häst", "att äta som en häst"),
    ("föda", "föda"),
    ("dramatik", "dramatik"),
    ("dramatiker", "dramatiker"),
    ("provsmaka", "provsmaka"),
    ("blodtörstig", "blodtörstig"),
    ("lättlagad", "lättlagad"),
    ("plockmat", "plockmat"),
    ("hämtmat", "hämtmat"),
    ("godis", "godis"),
    ("smågodis", "smågodis"),
    ("äpple", "äpple"),
    ("socker", "socker"),
    ("Ska vi ta en fika?", "Ska vi ta en fika?"),

    # Glue
    ("för en stund", "För en stund"),
    ("nivå", "nivå"),
    ("tom", "tom"),
    ("hellre … än", "hellre baka en kaka än"),
    ("trång", "trång"),
    ("nästnästa", "nästnästa"),
    ("försvinna", "försvinna"),
    ("ntally", "ntally"),
    ("Det är inte sant!", "Det är inte sant!"),
    ("obekväm", "obekväm"),
    ("getingstick", "getingstick"),
    ("Istället för att…", "Istället för att…"),
    ("kritisk", "kritisk"),
    ("sprida sig", "sprida sig"),
    ("vara säker på", "vara säker på"),
    ("misslyckande", "misslyckande"),
    ("var och en", "Var och en"),
    ("kommentar", "kommentar"),
    ("sakna", "sakna"),
    ("år", "år"),
    ("efter att ha", "Efter att ha"),
    ("liknande", "liknande")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if base == "baka":
        start = text.find("att baka och") + 4
    elif base == "drink":
        start = text.find("en drink,") + 3
    elif base == "mat":
        start = text.find("älskar mat.") + 7
    elif base == "godis":
        start = text.find("köpt godis") + 5
    elif " " in word_in_sentence or "." in word_in_sentence or "?" in word_in_sentence or "!" in word_in_sentence or "…" in word_in_sentence:
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
    "step_id": "mat_matlagning",
    "step_title": "Mat & Matlagning",
    "article_id": "art_12",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('course/sfid/phase2/article_12.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
