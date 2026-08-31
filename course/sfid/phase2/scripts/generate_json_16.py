import json
import re

text = """"Läget?" frågade min granne när han bestämde sig för att titta in en kall kväll i mars. "Tror du att…?" började han, men stannade. Jag förstod vad han skulle mena. Han var jättehungrig.

Jag hade en idé om att laga en värmande soppa. "Vi borde äta något gott," sa jag. Jag började laga mat framför en glittrande brasa. Ett faktum är att jag älskar närproducerad och närodlad mat. Jag ville ta reda på om han gillade klassisk svensk husmanskost, så att han fick uppleva riktig tradition.

Först bjöd jag på soppa på gul ärta med stekt fläsk. Vissa kryddar den med tyska örter, men jag hade i lite vitlök och ingefära. En unge hade nog tyckt det var konstigt, men han tyckte om det. Min granne verkade inte vara smittad av någon förkylning, för han hade en god aptit. Han förklarade i detalj varför det var den bästa måltiden på länge. Som konsekvens fick jag laga ännu mer!

Till huvudrätt bjöd jag på en maträtt som var en kåldolme fylld med ris och kött. Vi hade också tärnad tomat och rå lök. Som tillbehör serverade jag ugnstekt lax med en klick gräddsås. 

Till efterrätt åt vi saffranspannkaka gjord av en fin smet med saffran och äggvita. Den serverades med salmbär och vispad grädde, samt lite russin. Det var en kaloririk men underbar efterrätt. Framför allt älskade han en liten riven persika på toppen, och lite konfekt att smälta i munnen. 

Vi drack varm choklad och kaffe latte. En stor mängd choklad fanns med. Jag lade i en liten flinga av choklad i kaffet. Han tog också en smörgås med krås från en gås – oftast äter man det på Mårten Gås, men varför kryssa över en bra sak bara för att det är fel årstid? Maten kunde dessutom innehålla lite konjak för smaken."""

core_words = [
    "ärta", "stekt", "konfekt", "fläsk", "russin", "äggvita", "vitlök", "flinga", 
    "soppa", "smet", "saffran", "närproducerad", "salmbär", "gräddsås", "maträtt", 
    "riven", "persika", "ugnstekt", "rå", "vispad", "lax", "kaffe latte", "tärnad", 
    "kåldolme", "ingefära", "saffranspannkaka", "varm choklad", "tomat", "smörgås", 
    "gås", "krås", "närodlad", "kaloririk", "gjord av", "konjak", "ris"
]

glue_words = [
    "titta in", "glittrande", "ta reda på", "unge", "smälta", "oftast", "borde", 
    "i detalj", "så att", "mena", "vara smittad av", "idé", "framför allt", "Läget?", 
    "mängd", "kryssa över", "faktum", "mars", "konsekvens", "brasa", "innehålla", 
    "tyska", "Tror du att…?", "uppleva"
]

target_mappings = [
    # Core
    ("ärta", "ärta"),
    ("stekt", "stekt"),
    ("konfekt", "konfekt"),
    ("fläsk", "fläsk"),
    ("russin", "russin"),
    ("äggvita", "äggvita"),
    ("vitlök", "vitlök"),
    ("flinga", "flinga"),
    ("soppa", "soppa"),
    ("smet", "smet"),
    ("saffran", "saffran"),
    ("närproducerad", "närproducerad"),
    ("salmbär", "salmbär"),
    ("gräddsås", "gräddsås"),
    ("maträtt", "maträtt"),
    ("riven", "riven"),
    ("persika", "persika"),
    ("ugnstekt", "ugnstekt"),
    ("rå", "rå"),
    ("vispad", "vispad"),
    ("lax", "lax"),
    ("kaffe latte", "kaffe latte"),
    ("tärnad", "tärnad"),
    ("kåldolme", "kåldolme"),
    ("ingefära", "ingefära"),
    ("saffranspannkaka", "saffranspannkaka"),
    ("varm choklad", "varm choklad"),
    ("tomat", "tomat"),
    ("smörgås", "smörgås"),
    ("gås", "gås"),
    ("krås", "krås"),
    ("närodlad", "närodlad"),
    ("kaloririk", "kaloririk"),
    ("gjord av", "gjord av"),
    ("konjak", "konjak"),
    ("ris", "ris"),

    # Glue
    ("titta in", "titta in"),
    ("glittrande", "glittrande"),
    ("ta reda på", "ta reda på"),
    ("unge", "unge"),
    ("smälta", "smälta"),
    ("oftast", "oftast"),
    ("borde", "borde"),
    ("i detalj", "i detalj"),
    ("så att", "så att"),
    ("mena", "mena"),
    ("vara smittad av", "vara smittad av"),
    ("idé", "idé"),
    ("framför allt", "Framför allt"),
    ("Läget?", "Läget?"),
    ("mängd", "mängd"),
    ("kryssa över", "kryssa över"),
    ("faktum", "faktum"),
    ("mars", "mars"),
    ("konsekvens", "konsekvens"),
    ("brasa", "brasa"),
    ("innehålla", "innehålla"),
    ("tyska", "tyska"),
    ("Tror du att…?", "Tror du att…?"),
    ("uppleva", "uppleva")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if base == "gås":
        start = text.find("en gås") + 3
    elif base == "soppa":
        start = text.find("värmande soppa") + 9
    elif base == "saffran":
        start = text.find("med saffran") + 4
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
        print(f"ERROR: could not find {word_in_sentence} for {base}")
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
    "article_id": "art_16",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('course/sfid/phase2/article_16.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
