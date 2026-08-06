import json

base_json = {
    "course_id": "sfid",
    "course_title": "SFI D",
    "stage_id": "stage_07",
    "stage_title": "Natur & Miljö",
    "article_id": "art_19",
    "article_title": "Ett Grönt Möte i Skogen",
    "target_word_count": 60,
    "sentences": [],
    "primary_words_used": [
        "hällristning", "kretslopp", "taggmoln", "Har du ätit det någon gång?",
        "Nej, det har jag aldrig gjort!", "korv", "havre", "mintgrön", "högkonjunktur",
        "avlopp", "jättestark", "få problem", "miljörörelse", "gröna vågen", "slå igenom",
        "miljö- och klimatdebatt", "klimat", "hinna med", "skydd mot", "ute i naturen",
        "dragen av sex hästar", "katolik", "abdikation", "apelsinträd", "abdikera",
        "stenhäll", "känna igen", "ha planer", "grönländska", "personlig tränare",
        "engagera sig i", "Har du hört vad XX gjort?", "Jag måste berätta en sak/en grej…",
        "Har du hört talas om …?", "Har du/ni hört att?", "missuppfattning", "guldfisk",
        "känd för att ha", "snöboll", "låta bli", "oskyldig", "–Hej! Det var länge sedan!",
        "ingen åsikt", "bestämd", "anfalla", "vara", "bland", "svida", "acceptera",
        "århundrade", "överdriva", "röd- och vitrandig", "Va?", "ung", "namn", "få tillbaka",
        "döpa", "lösvikt", "klick", "motivera"
    ],
    "secondary_words_used": []
}

sentences_data = [
    {
        "sv": "\"–Hej! Det var länge sedan!\" sa jag när jag mötte min gamla vän i skogen.",
        "en": "\"Hello! It's been a long time!\" I said when I met my old friend in the forest.",
        "targets": [("–Hej! Det var länge sedan!", "–Hej! Det var länge sedan!")],
        "seconds": [("skogen", "skog", "the forest"), ("mötte", "möta", "met")]
    },
    {
        "sv": "\"Va?\" sa hon.",
        "en": "\"What?\" she said.",
        "targets": [("Va?", "Va?")],
        "seconds": [("sa", "säga", "said")]
    },
    {
        "sv": "Sedan kände hon igen mig.",
        "en": "Then she recognized me.",
        "targets": [("kände hon igen", "känna igen")],
        "seconds": [("sedan", "sedan", "then")]
    },
    {
        "sv": "\"Jag måste berätta en sak/en grej…\" började hon.",
        "en": "\"I have to tell you something/a thing...\" she started.",
        "targets": [("Jag måste berätta en sak/en grej…", "Jag måste berätta en sak/en grej…")],
        "seconds": [("började", "börja", "started")]
    },
    {
        "sv": "\"Har du hört vad XX gjort?\" frågade hon och log.",
        "en": "\"Have you heard what XX did?\" she asked and smiled.",
        "targets": [("Har du hört vad XX gjort?", "Har du hört vad XX gjort?")],
        "seconds": [("log", "le", "smiled")]
    },
    {
        "sv": "\"Nej, jag har ingen åsikt om kändisar,\" svarade jag bestämt.",
        "en": "\"No, I have no opinion about celebrities,\" I answered firmly.",
        "targets": [("ingen åsikt", "ingen åsikt"), ("bestämt", "bestämd")],
        "seconds": [("kändisar", "kändis", "celebrities"), ("svarade", "svara", "answered")]
    },
    {
        "sv": "\"Har du/ni hört att?\" skämtade hon, \"han ska ha planer på att abdikera från sitt jobb som personlig tränare!\"",
        "en": "\"Have you heard that?\" she joked, \"he allegedly has plans to abdicate from his job as a personal trainer!\"",
        "targets": [("Har du/ni hört att?", "Har du/ni hört att?"), ("ha planer", "ha planer"), ("abdikera", "abdikera"), ("personlig tränare", "personlig tränare")],
        "seconds": [("skämtade", "skämta", "joked"), ("jobb", "jobb", "job")]
    },
    {
        "sv": "Hennes berättelse kändes som en rolig abdikation från allvaret, men det var skönt att vara ute i naturen.",
        "en": "Her story felt like a fun abdication from seriousness, but it was nice to be out in nature.",
        "targets": [("abdikation", "abdikation"), ("vara", "vara"), ("ute i naturen", "ute i naturen")],
        "seconds": [("berättelse", "berättelse", "story"), ("skönt", "skön", "nice")]
    },
    {
        "sv": "\"Har du hört talas om …?\" frågade hon och pekade på en gammal stenhäll.",
        "en": "\"Have you heard of...?\" she asked and pointed at an old rock slab.",
        "targets": [("Har du hört talas om …?", "Har du hört talas om …?"), ("stenhäll", "stenhäll")],
        "seconds": [("pekade", "peka", "pointed"), ("gammal", "gammal", "old")]
    },
    {
        "sv": "\"Där finns en hällristning från ett tidigt århundrade.",
        "en": "\"There is a petroglyph from an early century.",
        "targets": [("hällristning", "hällristning"), ("århundrade", "århundrade")],
        "seconds": [("tidigt", "tidig", "early")]
    },
    {
        "sv": "Det fanns en katolik som var känd för att ha rest hit dragen av sex hästar.\"",
        "en": "There was a Catholic who was known to have traveled here drawn by six horses.\"",
        "targets": [("katolik", "katolik"), ("känd för att ha", "känd för att ha"), ("dragen av sex hästar", "dragen av sex hästar")],
        "seconds": [("rest", "resa", "traveled")]
    },
    {
        "sv": "Hon hade en röd- och vitrandig jacka och en mintgrön mössa.",
        "en": "She had a red- and white-striped jacket and a mint green beanie.",
        "targets": [("röd- och vitrandig", "röd- och vitrandig"), ("mintgrön", "mintgrön")],
        "seconds": [("jacka", "jacka", "jacket"), ("mössa", "mössa", "beanie")]
    },
    {
        "sv": "Vi satte oss bland träden.",
        "en": "We sat down among the trees.",
        "targets": [("bland", "bland")],
        "seconds": [("träden", "träd", "the trees")]
    },
    {
        "sv": "\"Det finns en missuppfattning om skogen.",
        "en": "\"There is a misconception about the forest.",
        "targets": [("missuppfattning", "missuppfattning")],
        "seconds": [("skogen", "skog", "the forest")]
    },
    {
        "sv": "Vissa tror att djur kommer att anfalla, men de är ofta oskyldiga,\" sa hon.",
        "en": "Some believe that animals will attack, but they are often innocent,\" she said.",
        "targets": [("anfalla", "anfalla"), ("oskyldiga", "oskyldig")],
        "seconds": [("djur", "djur", "animals")]
    },
    {
        "sv": "Vi köpte lite godis i lösvikt och lade en klick sylt på en bit bröd.",
        "en": "We bought some candy in bulk and put a dollop of jam on a piece of bread.",
        "targets": [("lösvikt", "lösvikt"), ("klick", "klick")],
        "seconds": [("godis", "godis", "candy"), ("bröd", "bröd", "bread")]
    },
    {
        "sv": "Hon frågade om min vegan-korv gjord på havre.",
        "en": "She asked about my vegan sausage made of oats.",
        "targets": [("korv", "korv"), ("havre", "havre")],
        "seconds": [("gjord", "gjord", "made")]
    },
    {
        "sv": "\"Har du ätit det någon gång?\" frågade jag.",
        "en": "\"Have you ever eaten that?\" I asked.",
        "targets": [("Har du ätit det någon gång?", "Har du ätit det någon gång?")],
        "seconds": [("frågade", "fråga", "asked")]
    },
    {
        "sv": "\"Nej, det har jag aldrig gjort!\" skrattade hon.",
        "en": "\"No, I have never done that!\" she laughed.",
        "targets": [("Nej, det har jag aldrig gjort!", "Nej, det har jag aldrig gjort!")],
        "seconds": [("skrattade", "skratta", "laughed")]
    },
    {
        "sv": "Hon kunde inte låta bli att smaka.",
        "en": "She couldn't resist tasting it.",
        "targets": [("låta bli", "låta bli")],
        "seconds": [("smaka", "smaka", "taste")]
    },
    {
        "sv": "Smaken var jättestark och fick hennes ögon att svida.",
        "en": "The taste was very strong and made her eyes sting.",
        "targets": [("jättestark", "jättestark"), ("svida", "svida")],
        "seconds": [("smaken", "smak", "the taste"), ("ögon", "öga", "eyes")]
    },
    {
        "sv": "Sedan pratade vi om vår natur.",
        "en": "Then we talked about our nature.",
        "targets": [],
        "seconds": [("pratade", "prata", "talked")]
    },
    {
        "sv": "\"På 70-talet under en högkonjunktur började den gröna vågen slå igenom.",
        "en": "\"In the 70s during an economic boom, the green wave started to break through.",
        "targets": [("högkonjunktur", "högkonjunktur"), ("gröna vågen", "gröna vågen"), ("slå igenom", "slå igenom")],
        "seconds": [("började", "börja", "started")]
    },
    {
        "sv": "Folk ville ha ett naturligt kretslopp för allt från regn till avlopp,\" sa hon.",
        "en": "People wanted a natural cycle for everything from rain to sewage,\" she said.",
        "targets": [("kretslopp", "kretslopp"), ("avlopp", "avlopp")],
        "seconds": [("regn", "regn", "rain")]
    },
    {
        "sv": "Idag är en modern miljörörelse viktig i varje miljö- och klimatdebatt.",
        "en": "Today a modern environmental movement is important in every environmental and climate debate.",
        "targets": [("miljörörelse", "miljörörelse"), ("miljö- och klimatdebatt", "miljö- och klimatdebatt")],
        "seconds": [("modern", "modern", "modern"), ("viktig", "viktig", "important")]
    },
    {
        "sv": "Ordet klimat syns i varje taggmoln online.",
        "en": "The word climate appears in every tag cloud online.",
        "targets": [("klimat", "klimat"), ("taggmoln", "taggmoln")],
        "seconds": [("syns", "synas", "appears"), ("ordet", "ord", "the word")]
    },
    {
        "sv": "Många unga vill engagera sig i miljön.",
        "en": "Many young people want to get involved in the environment.",
        "targets": [("unga", "ung"), ("engagera sig i", "engagera sig i")],
        "seconds": [("miljön", "miljö", "the environment")]
    },
    {
        "sv": "Även min lilla guldfisk verkar vilja ha rent vatten!",
        "en": "Even my little goldfish seems to want clean water!",
        "targets": [("guldfisk", "guldfisk")],
        "seconds": [("rent", "ren", "clean")]
    },
    {
        "sv": "\"Det är svårt att hinna med att bygga ett starkt skydd mot föroreningar, men vi måste motivera fler att acceptera fakta och inte överdriva rädslan,\" sa hon.",
        "en": "\"It is hard to keep up with building strong protection against pollution, but we must motivate more people to accept facts and not exaggerate fear,\" she said.",
        "targets": [("hinna med", "hinna med"), ("skydd mot", "skydd mot"), ("motivera", "motivera"), ("acceptera", "acceptera"), ("överdriva", "överdriva")],
        "seconds": [("bygga", "bygga", "build"), ("fakta", "fakta", "facts")]
    },
    {
        "sv": "Ibland känns det som om vi pratar på grönländska, ingen förstår varandra.",
        "en": "Sometimes it feels like we are talking in Greenlandic, nobody understands each other.",
        "targets": [("grönländska", "grönländska")],
        "seconds": [("ibland", "ibland", "sometimes"), ("förstår", "förstå", "understands")]
    },
    {
        "sv": "Ett namn på problemet är okunskap.",
        "en": "One name for the problem is ignorance.",
        "targets": [("namn", "namn")],
        "seconds": [("problemet", "problem", "the problem"), ("okunskap", "okunskap", "ignorance")]
    },
    {
        "sv": "Det kändes bra att döpa problemen och förhoppningsvis få tillbaka hoppet.",
        "en": "It felt good to name the problems and hopefully get hope back.",
        "targets": [("döpa", "döpa"), ("få tillbaka", "få tillbaka")],
        "seconds": [("hoppet", "hopp", "the hope")]
    },
    {
        "sv": "Innan vi gick kastade vi en snöboll mot ett litet apelsinträd i ett växthus.",
        "en": "Before we left, we threw a snowball at a small orange tree in a greenhouse.",
        "targets": [("snöboll", "snöboll"), ("apelsinträd", "apelsinträd")],
        "seconds": [("kastade", "kasta", "threw"), ("växthus", "växthus", "greenhouse")]
    },
    {
        "sv": "Vi riskerar att få problem om vi inte agerar, men vi kämpar på!",
        "en": "We risk getting into trouble if we do not act, but we keep fighting!",
        "targets": [("få problem", "få problem")],
        "seconds": [("riskerar", "riskera", "risk"), ("kämpar", "kämpa", "fight")]
    }
]

for i, sd in enumerate(sentences_data):
    sentence = {
        "sentence_id": f"art_19_s{i+1:03d}",
        "sv": sd["sv"],
        "en": sd["en"],
        "target_words": [
            {
                "word_in_sentence": t[0],
                "base_form": t[1],
                "contextual_en": ""  # omitted for simplicity or could guess
            } for t in sd["targets"]
        ],
        "secondary_words": [
            {
                "word_in_sentence": s[0],
                "base_form": s[1],
                "contextual_en": s[2]
            } for s in sd["seconds"]
        ]
    }
    base_json["sentences"].append(sentence)

import os
path1 = "course/sfid/phase2/articles_translated/art_19.json"
path2 = "course/sfid/phase2/articles/article_19.json"

with open(path1, "w", encoding="utf-8") as f:
    json.dump(base_json, f, ensure_ascii=False, indent=4)

if os.path.exists(path2):
    with open(path2, "w", encoding="utf-8") as f:
        json.dump(base_json, f, ensure_ascii=False, indent=4)
else:
    print(f"Warning: {path2} does not exist. Creating it.")
    os.makedirs(os.path.dirname(path2), exist_ok=True)
    with open(path2, "w", encoding="utf-8") as f:
        json.dump(base_json, f, ensure_ascii=False, indent=4)

print("art_19 successfully reconstructed and saved!")
