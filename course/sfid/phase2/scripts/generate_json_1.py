import json
import re

text = """När du går till jobbet är det säkert en vanlig rutin att sätta på datorn som det allra första du gör. Men har du någonsin funderat över hur allting inuti maskinen egentligen fungerar? Innan jag valde att gå en praktisk datakurs visste jag nästan ingenting om den moderna teknikens detaljer. Nu förstår jag att det handlar om mer än bara en enkel skärm; det är ett helt system av information.

Varje år försöker tusentals experter att uppfinna ny utrustning som ska göra våra liv enklare. En mycket känd vetenskapsman arbetade för många hundra år sedan med att observera och systematisera ny kunskap. Genom att använda en speciell och noggrann metod kunde han snabbt beräkna avstånd i rymden och uppmäta exakta temperaturer. Han studerade ofta stjärnornas ljus noga genom ett stort teleskop. Han var en riktigt duktig astronom som varje kväll stod och tittade upp mot en vacker stjärnhimmel. I mitten av det mörka rummet stod hans fina arbetsverktyg.

Forskning är inte alltid en lätt process. Ofta sker en osynlig maktkamp mellan olika nya idéer, där en oprövad teori måste stå mot en annan. Forskare bygger alltid sitt hårda arbete på riktig fakta, inte på fantasier. De flesta är djupt intresserade av att lösa svåra problem för att på bästa sätt hjälpa varandra. Enligt svensk statistik är resultatet säkert till hundra procent. Faktum är att cirka tjugo procent av försöken kanske misslyckas, men man lär sig otroligt mycket av dem också.

I dag lever vi i en värld där vi ständigt är uppkopplade mot internet. Det finns någon typ av elektrisk liten motor i nästan alla våra maskiner hemma. Vi kan i dag simulera mycket komplicerade processer direkt på skärmen, långt före vi bygger dem i verkligheten. Detta moderna arbete kräver ibland hög intelligens och en fantastisk intellektuell förmåga. Man kan nu sitta bekvämt och titta igenom information från hela jorden, helt utan att lämna sin stol.

I genomsnitt spenderar moderna människor mycket tid online. En ganska vanlig fråga är om vi utvecklas för fort, eller om vi tvärtom är för långsamma. Oavsett vad vi kan tycka om saken, fortsätter tekniken att gå framåt. Du kan mäta ett föremåls längd, vikt och bredd, men framtiden är svårare att mäta. Vi kan bland annat se att vår populära teknik, inklusive våra telefoner, är det mest användbara vi har. Du kan lugnt avsluta din dag med att visa roliga filmer, sen är du redo för nästa spännande dag."""

core_words = [
    "sätta på datorn", "maktkamp", "datakurs", "uppfinna", "uppmäta", "beräkna", 
    "uppkopplad", "procent av", "intelligens", "intellektuell", "längd", "procent", 
    "genomsnitt", "metod", "elektrisk", "fakta", "teori", "systematisera", "teleskop", 
    "astronom", "motor", "vetenskapsman", "simulera"
]

glue_words = [
    "avsluta", "lämna", "din", "igenom", "sen", "titta", "vacker", "speciell", "genom", 
    "populär", "allting", "före", "mitten", "typ", "upp", "över", "måste", "ingenting", 
    "långsam", "de flesta", "tycka", "av", "visa", "nästa", "bland annat", "varandra", 
    "enligt", "inklusive", "mer än", "fråga", "nästan", "eller", "för", "mest", "varje", 
    "också", "mycket"
]

target_mappings = [
    ("sätta på datorn", "sätta på datorn"),
    ("maktkamp", "maktkamp"),
    ("datakurs", "datakurs"),
    ("uppfinna", "uppfinna"),
    ("uppmäta", "uppmäta"),
    ("beräkna", "beräkna"),
    ("uppkopplad", "uppkopplade"),
    ("procent av", "procent av"),
    ("intelligens", "intelligens"),
    ("intellektuell", "intellektuell"),
    ("längd", "längd"),
    ("procent", "procent"),
    ("genomsnitt", "genomsnitt"),
    ("metod", "metod"),
    ("elektrisk", "elektrisk"),
    ("fakta", "fakta"),
    ("teori", "teori"),
    ("systematisera", "systematisera"),
    ("teleskop", "teleskop"),
    ("astronom", "astronom"),
    ("motor", "motor"),
    ("vetenskapsman", "vetenskapsman"),
    ("simulera", "simulera"),
    
    ("avsluta", "avsluta"),
    ("lämna", "lämna"),
    ("din", "din"),
    ("igenom", "igenom"),
    ("sen", "sen"),
    ("titta", "titta"),
    ("vacker", "vacker"),
    ("speciell", "speciell"),
    ("genom", "Genom"),
    ("populär", "populära"),
    ("allting", "allting"),
    ("före", "före"),
    ("mitten", "mitten"),
    ("typ", "typ"),
    ("upp", "upp"),
    ("över", "över"),
    ("måste", "måste"),
    ("ingenting", "ingenting"),
    ("långsam", "långsamma"),
    ("de flesta", "De flesta"),
    ("tycka", "tycka"),
    ("av", "av"),
    ("visa", "visa"),
    ("nästa", "nästa"),
    ("bland annat", "bland annat"),
    ("varandra", "varandra"),
    ("enligt", "Enligt"),
    ("inklusive", "inklusive"),
    ("mer än", "mer än"),
    ("fråga", "fråga"),
    ("nästan", "nästan"),
    ("eller", "eller"),
    ("för", "för"),
    ("mest", "mest"),
    ("varje", "Varje"),
    ("också", "också"),
    ("mycket", "mycket")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if " " in word_in_sentence:
        start = text.find(word_in_sentence)
    else:
        escaped = re.escape(word_in_sentence)
        match = re.search(r'\b' + escaped + r'\b', text)
        if match:
            start = match.start()
        else:
            start = text.find(word_in_sentence)
            
    if start == -1:
        print(f"ERROR: could not find {word_in_sentence}")
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
    "step_id": "vetenskap_teknik",
    "step_title": "Vetenskap & Teknik",
    "article_id": "art_01",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('course/sfid/phase2/article_1.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
