import json

sentences_data = [
    {
        "sv": "\"–Hej! Det var länge sedan!\" sa jag när jag mötte min gamla vän i skogen.",
        "en": "\"Hello! It's been a long time!\" I said when I met my old friend in the forest.",
        "target_words": ["–Hej! Det var länge sedan!"],
        "secondary_words": [
            {"word_in_sentence": "mötte", "base_form": "möta", "contextual_en": "met"},
            {"word_in_sentence": "skogen", "base_form": "skog", "contextual_en": "the forest"}
        ]
    },
    {
        "sv": "\"Va?\" sa hon.",
        "en": "\"What?\" she said.",
        "target_words": ["Va?"],
        "secondary_words": [
            {"word_in_sentence": "sa", "base_form": "säga", "contextual_en": "said"}
        ]
    },
    {
        "sv": "Sedan kände hon igen mig.",
        "en": "Then she recognized me.",
        "target_words": ["känna igen"],
        "secondary_words": [
            {"word_in_sentence": "Sedan", "base_form": "sedan", "contextual_en": "Then"}
        ]
    },
    {
        "sv": "\"Jag måste berätta en sak/en grej…\" började hon.",
        "en": "\"I have to tell you something/a thing...\" she began.",
        "target_words": ["Jag måste berätta en sak/en grej…"],
        "secondary_words": [
            {"word_in_sentence": "började", "base_form": "börja", "contextual_en": "began"}
        ]
    },
    {
        "sv": "\"Har du hört vad XX gjort?\" frågade hon och log.",
        "en": "\"Have you heard what XX did?\" she asked and smiled.",
        "target_words": ["Har du hört vad XX gjort?"],
        "secondary_words": [
            {"word_in_sentence": "frågade", "base_form": "fråga", "contextual_en": "asked"},
            {"word_in_sentence": "log", "base_form": "le", "contextual_en": "smiled"}
        ]
    },
    {
        "sv": "\"Nej, jag har ingen åsikt om kändisar,\" svarade jag bestämt.",
        "en": "\"No, I have no opinion about celebrities,\" I answered firmly.",
        "target_words": ["ingen åsikt", "bestämd"],
        "secondary_words": [
            {"word_in_sentence": "kändisar", "base_form": "kändis", "contextual_en": "celebrities"},
            {"word_in_sentence": "svarade", "base_form": "svara", "contextual_en": "answered"}
        ]
    },
    {
        "sv": "\"Har du/ni hört att?\" skämtade hon, \"han ska ha planer på att abdikera från sitt jobb som personlig tränare!\"",
        "en": "\"Have you heard that?\" she joked, \"he supposedly has plans to abdicate from his job as a personal trainer!\"",
        "target_words": ["Har du/ni hört att?", "ha planer", "abdikera", "personlig tränare"],
        "secondary_words": [
            {"word_in_sentence": "skämtade", "base_form": "skämta", "contextual_en": "joked"},
            {"word_in_sentence": "jobb", "base_form": "jobb", "contextual_en": "job"}
        ]
    },
    {
        "sv": "Hennes berättelse kändes som en rolig abdikation från allvaret, men det var skönt att vara ute i naturen.",
        "en": "Her story felt like a fun abdication from seriousness, but it was nice to be out in nature.",
        "target_words": ["abdikation", "vara", "ute i naturen"],
        "secondary_words": [
            {"word_in_sentence": "berättelse", "base_form": "berättelse", "contextual_en": "story"},
            {"word_in_sentence": "allvaret", "base_form": "allvar", "contextual_en": "the seriousness"},
            {"word_in_sentence": "skönt", "base_form": "skön", "contextual_en": "nice"}
        ]
    },
    {
        "sv": "\"Har du hört talas om …?\" frågade hon och pekade på en gammal stenhäll.",
        "en": "\"Have you heard of...?\" she asked and pointed at an old rock slab.",
        "target_words": ["Har du hört talas om …?", "stenhäll"],
        "secondary_words": [
            {"word_in_sentence": "pekade", "base_form": "peka", "contextual_en": "pointed"},
            {"word_in_sentence": "gammal", "base_form": "gammal", "contextual_en": "old"}
        ]
    },
    {
        "sv": "\"Där finns en hällristning från ett tidigt århundrade.",
        "en": "\"There is a petroglyph from an early century.",
        "target_words": ["hällristning", "århundrade"],
        "secondary_words": [
            {"word_in_sentence": "tidigt", "base_form": "tidig", "contextual_en": "early"}
        ]
    },
    {
        "sv": "Det fanns en katolik som var känd för att ha rest hit dragen av sex hästar.\"",
        "en": "There was a Catholic who was known for having traveled here drawn by six horses.\"",
        "target_words": ["katolik", "känd för att ha", "dragen av sex hästar"],
        "secondary_words": [
            {"word_in_sentence": "rest", "base_form": "resa", "contextual_en": "traveled"},
            {"word_in_sentence": "hit", "base_form": "hit", "contextual_en": "here"}
        ]
    },
    {
        "sv": "Hon hade en röd- och vitrandig jacka och en mintgrön mössa.",
        "en": "She had a red and white striped jacket and a mint green beanie.",
        "target_words": ["röd- och vitrandig", "mintgrön"],
        "secondary_words": [
            {"word_in_sentence": "jacka", "base_form": "jacka", "contextual_en": "jacket"},
            {"word_in_sentence": "mössa", "base_form": "mössa", "contextual_en": "beanie"}
        ]
    },
    {
        "sv": "Vi satte oss bland träden.",
        "en": "We sat down among the trees.",
        "target_words": ["bland"],
        "secondary_words": [
            {"word_in_sentence": "satte oss", "base_form": "sätta sig", "contextual_en": "sat down"},
            {"word_in_sentence": "träden", "base_form": "träd", "contextual_en": "the trees"}
        ]
    },
    {
        "sv": "\"Det finns en missuppfattning om skogen.",
        "en": "\"There is a misconception about the forest.",
        "target_words": ["missuppfattning"],
        "secondary_words": [
            {"word_in_sentence": "finns", "base_form": "finnas", "contextual_en": "is/exists"}
        ]
    },
    {
        "sv": "Vissa tror att djur kommer att anfalla, men de är ofta oskyldiga,\" sa hon.",
        "en": "Some think that animals will attack, but they are often innocent,\" she said.",
        "target_words": ["anfalla", "oskyldig"],
        "secondary_words": [
            {"word_in_sentence": "tror", "base_form": "tro", "contextual_en": "think/believe"},
            {"word_in_sentence": "ofta", "base_form": "ofta", "contextual_en": "often"}
        ]
    },
    {
        "sv": "Vi köpte lite godis i lösvikt och lade en klick sylt på en bit bröd.",
        "en": "We bought some loose candy and put a dollop of jam on a piece of bread.",
        "target_words": ["lösvikt", "klick"],
        "secondary_words": [
            {"word_in_sentence": "godis", "base_form": "godis", "contextual_en": "candy"},
            {"word_in_sentence": "sylt", "base_form": "sylt", "contextual_en": "jam"},
            {"word_in_sentence": "bröd", "base_form": "bröd", "contextual_en": "bread"}
        ]
    },
    {
        "sv": "Hon frågade om min vegan-korv gjord på havre.",
        "en": "She asked about my vegan sausage made of oats.",
        "target_words": ["korv", "havre"],
        "secondary_words": [
            {"word_in_sentence": "gjord", "base_form": "gjord", "contextual_en": "made"}
        ]
    },
    {
        "sv": "\"Har du ätit det någon gång?\" frågade jag.",
        "en": "\"Have you eaten it ever?\" I asked.",
        "target_words": ["Har du ätit det någon gång?"],
        "secondary_words": [
            {"word_in_sentence": "ätit", "base_form": "äta", "contextual_en": "eaten"}
        ]
    },
    {
        "sv": "\"Nej, det har jag aldrig gjort!\" skrattade hon.",
        "en": "\"No, I have never done that!\" she laughed.",
        "target_words": ["Nej, det har jag aldrig gjort!"],
        "secondary_words": [
            {"word_in_sentence": "skrattade", "base_form": "skratta", "contextual_en": "laughed"}
        ]
    },
    {
        "sv": "Hon kunde inte låta bli att smaka.",
        "en": "She couldn't help but taste it.",
        "target_words": ["låta bli"],
        "secondary_words": [
            {"word_in_sentence": "kunde", "base_form": "kunna", "contextual_en": "could"},
            {"word_in_sentence": "smaka", "base_form": "smaka", "contextual_en": "taste"}
        ]
    },
    {
        "sv": "Smaken var jättestark och fick hennes ögon att svida.",
        "en": "The taste was extremely strong and made her eyes sting.",
        "target_words": ["jättestark", "svida"],
        "secondary_words": [
            {"word_in_sentence": "Smaken", "base_form": "smak", "contextual_en": "The taste"},
            {"word_in_sentence": "ögon", "base_form": "öga", "contextual_en": "eyes"}
        ]
    },
    {
        "sv": "Sedan pratade vi om vår natur.",
        "en": "Then we talked about our nature.",
        "target_words": [],
        "secondary_words": [
            {"word_in_sentence": "pratade", "base_form": "prata", "contextual_en": "talked"},
            {"word_in_sentence": "natur", "base_form": "natur", "contextual_en": "nature"}
        ]
    },
    {
        "sv": "\"På 70-talet under en högkonjunktur började den gröna vågen slå igenom.",
        "en": "\"In the 70s during an economic boom, the green wave started to break through.",
        "target_words": ["högkonjunktur", "gröna vågen", "slå igenom"],
        "secondary_words": [
            {"word_in_sentence": "under", "base_form": "under", "contextual_en": "during"}
        ]
    },
    {
        "sv": "Folk ville ha ett naturligt kretslopp för allt från regn till avlopp,\" sa hon.",
        "en": "People wanted a natural cycle for everything from rain to sewage,\" she said.",
        "target_words": ["kretslopp", "avlopp"],
        "secondary_words": [
            {"word_in_sentence": "naturligt", "base_form": "naturlig", "contextual_en": "natural"},
            {"word_in_sentence": "regn", "base_form": "regn", "contextual_en": "rain"}
        ]
    },
    {
        "sv": "Idag är en modern miljörörelse viktig i varje miljö- och klimatdebatt.",
        "en": "Today, a modern environmental movement is important in every environmental and climate debate.",
        "target_words": ["miljörörelse", "miljö- och klimatdebatt"],
        "secondary_words": [
            {"word_in_sentence": "modern", "base_form": "modern", "contextual_en": "modern"},
            {"word_in_sentence": "viktig", "base_form": "viktig", "contextual_en": "important"}
        ]
    },
    {
        "sv": "Ordet klimat syns i varje taggmoln online.",
        "en": "The word climate is seen in every tag cloud online.",
        "target_words": ["climate", "taggmoln"],
        "secondary_words": [
            {"word_in_sentence": "Ordet", "base_form": "ord", "contextual_en": "The word"},
            {"word_in_sentence": "syns", "base_form": "synas", "contextual_en": "is seen"}
        ]
    },
    {
        "sv": "Många unga vill engagera sig i miljön.",
        "en": "Many young people want to get involved in the environment.",
        "target_words": ["ung", "engagera sig i"],
        "secondary_words": [
            {"word_in_sentence": "Många", "base_form": "många", "contextual_en": "Many"},
            {"word_in_sentence": "miljön", "base_form": "miljö", "contextual_en": "the environment"}
        ]
    },
    {
        "sv": "Även min lilla guldfisk verkar vilja ha rent vatten!",
        "en": "Even my little goldfish seems to want clean water!",
        "target_words": ["guldfisk"],
        "secondary_words": [
            {"word_in_sentence": "verkar", "base_form": "verka", "contextual_en": "seems"},
            {"word_in_sentence": "rent", "base_form": "ren", "contextual_en": "clean"},
            {"word_in_sentence": "vatten", "base_form": "vatten", "contextual_en": "water"}
        ]
    },
    {
        "sv": "\"Det är svårt att hinna med att bygga ett starkt skydd mot föroreningar, men vi måste motivera fler att acceptera fakta och inte överdriva rädslan,\" sa hon.",
        "en": "\"It is difficult to have time to build a strong protection against pollution, but we must motivate more people to accept facts and not exaggerate the fear,\" she said.",
        "target_words": ["hinna med", "skydd mot", "motivera", "acceptera", "överdriva"],
        "secondary_words": [
            {"word_in_sentence": "svårt", "base_form": "svår", "contextual_en": "difficult"},
            {"word_in_sentence": "bygga", "base_form": "bygga", "contextual_en": "build"},
            {"word_in_sentence": "föroreningar", "base_form": "förorening", "contextual_en": "pollution"}
        ]
    },
    {
        "sv": "Ibland känns det som om vi pratar på grönländska, ingen förstår varandra.",
        "en": "Sometimes it feels like we are speaking in Greenlandic, nobody understands each other.",
        "target_words": ["grönländska"],
        "secondary_words": [
            {"word_in_sentence": "Ibland", "base_form": "ibland", "contextual_en": "Sometimes"},
            {"word_in_sentence": "förstår", "base_form": "förstå", "contextual_en": "understands"}
        ]
    },
    {
        "sv": "Ett namn på problemet är okunskap.",
        "en": "A name for the problem is ignorance.",
        "target_words": ["namn"],
        "secondary_words": [
            {"word_in_sentence": "problemet", "base_form": "problem", "contextual_en": "the problem"},
            {"word_in_sentence": "okunskap", "base_form": "okunskap", "contextual_en": "ignorance"}
        ]
    },
    {
        "sv": "Det kändes bra att döpa problemen och förhoppningsvis få tillbaka hoppet.",
        "en": "It felt good to name the problems and hopefully get the hope back.",
        "target_words": ["döpa", "få tillbaka"],
        "secondary_words": [
            {"word_in_sentence": "förhoppningsvis", "base_form": "förhoppningsvis", "contextual_en": "hopefully"},
            {"word_in_sentence": "hoppet", "base_form": "hopp", "contextual_en": "the hope"}
        ]
    },
    {
        "sv": "Innan vi gick kastade vi en snöboll mot ett litet apelsinträd i ett växthus.",
        "en": "Before we left, we threw a snowball at a small orange tree in a greenhouse.",
        "target_words": ["snöboll", "apelsinträd"],
        "secondary_words": [
            {"word_in_sentence": "kastade", "base_form": "kasta", "contextual_en": "threw"},
            {"word_in_sentence": "växthus", "base_form": "växthus", "contextual_en": "greenhouse"}
        ]
    },
    {
        "sv": "Vi riskerar att få problem om vi inte agerar, men vi kämpar på!",
        "en": "We risk getting into trouble if we don't act, but we keep fighting!",
        "target_words": ["få problem"],
        "secondary_words": [
            {"word_in_sentence": "riskerar", "base_form": "riskera", "contextual_en": "risk"},
            {"word_in_sentence": "agerar", "base_form": "agera", "contextual_en": "act"},
            {"word_in_sentence": "kämpar", "base_form": "kämpa", "contextual_en": "fight"}
        ]
    }
]

def find_word_in_sentence(sv_text, base_form):
    lower_sv = sv_text.lower()
    mapping = {
        "känna igen": "kände hon igen",
        "bestämd": "bestämt",
        "oskyldig": "oskyldiga",
        "climate": "klimat",
        "ung": "unga",
    }
    if base_form in mapping:
        return mapping[base_form]
    if base_form.lower() in lower_sv:
        idx = lower_sv.find(base_form.lower())
        return sv_text[idx:idx+len(base_form)]
    return base_form 

translated_json_path = "course/sfid/phase2/articles_translated/art_19.json"
articles_json_path = "course/sfid/phase2/articles/article_19.json"

with open(translated_json_path, 'r', encoding='utf-8') as f:
    translated_data = json.load(f)

new_sentences_translated = []
new_sentences_articles = []

for i, s_data in enumerate(sentences_data):
    s_id = f"art_19_s{i+1:03d}"
    
    t_words_translated = []
    t_words_articles = []
    for base in s_data["target_words"]:
        w_in_s = find_word_in_sentence(s_data["sv"], base)
        t_words_translated.append({
            "word_in_sentence": w_in_s,
            "base_form": base,
            "contextual_en": ""
        })
        t_words_articles.append({
            "word_in_sentence": w_in_s,
            "base_form": base
        })
        
    new_sentences_translated.append({
        "sentence_id": s_id,
        "sv": s_data["sv"],
        "en": s_data["en"],
        "target_words": t_words_translated,
        "secondary_words": s_data["secondary_words"]
    })
    
    new_sentences_articles.append({
        "sentence_id": s_id,
        "sv": s_data["sv"],
        "target_words": t_words_articles
    })

translated_data["sentences"] = new_sentences_translated
with open(translated_json_path, 'w', encoding='utf-8') as f:
    json.dump(translated_data, f, ensure_ascii=False, indent=4)

try:
    with open(articles_json_path, 'r', encoding='utf-8') as f:
        articles_data = json.load(f)
except FileNotFoundError:
    articles_data = translated_data.copy()
    if "secondary_words_used" in articles_data:
        del articles_data["secondary_words_used"]

articles_data["sentences"] = new_sentences_articles
with open(articles_json_path, 'w', encoding='utf-8') as f:
    json.dump(articles_data, f, ensure_ascii=False, indent=4)

print("art_19 correctly processed.")
