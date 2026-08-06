import json

art_19_path = "./course/sfid/phase2/articles_translated/art_19.json"
article_19_path = "./course/sfid/phase2/articles/article_19.json"

mapping = {
    "art_19_s001": {"–Hej! Det var länge sedan!": "Hello! It's been a long time!"},
    "art_19_s002": {"Va?": "What?"},
    "art_19_s003": {"kände hon igen": "recognized"},
    "art_19_s005": {"Har du hört vad XX gjort?": "Have you heard what XX did?"},
    "art_19_s006": {"ingen åsikt": "no opinion", "bestämt": "firmly"},
    "art_19_s007": {"ha planer": "has plans", "abdikera": "abdicate", "personlig tränare": "personal trainer"},
    "art_19_s008": {"abdikation": "abdication", "vara": "to be", "ute i naturen": "out in nature"},
    "art_19_s009": {"Har du hört talas om …?": "Have you heard of...?", "stenhäll": "rock slab"},
    "art_19_s010": {"hällristning": "petroglyph", "århundrade": "century"},
    "art_19_s011": {"katolik": "Catholic", "känd för att ha": "known to have", "dragen av sex hästar": "drawn by six horses"},
    "art_19_s012": {"röd- och vitrandig": "red- and white-striped", "mintgrön": "mint green"},
    "art_19_s013": {"bland": "among"},
    "art_19_s014": {"missuppfattning": "misconception"},
    "art_19_s015": {"anfalla": "attack", "oskyldiga": "innocent"},
    "art_19_s016": {"lösvikt": "in bulk", "klick": "dollop"},
    "art_19_s017": {"korv": "sausage", "havre": "oats"},
    "art_19_s018": {"Har du ätit det någon gång?": "Have you ever eaten that?"},
    "art_19_s019": {"Nej, det har jag aldrig gjort!": "No, I have never done that!"},
    "art_19_s020": {"låta bli": "resist"},
    "art_19_s021": {"jättestark": "very strong", "svida": "sting"},
    "art_19_s023": {"högkonjunktur": "economic boom", "gröna vågen": "green wave", "slå igenom": "break through"},
    "art_19_s024": {"kretslopp": "cycle", "avlopp": "sewage"},
    "art_19_s025": {"miljörörelse": "environmental movement", "miljö- och klimatdebatt": "environmental and climate debate"},
    "art_19_s026": {"klimat": "climate", "taggmoln": "tag cloud"},
    "art_19_s027": {"unga": "young people", "engagera sig i": "get involved in"},
    "art_19_s028": {"guldfisk": "goldfish"},
    "art_19_s029": {"hinna med": "keep up with", "skydd mot": "protection against", "motivera": "motivate", "acceptera": "accept", "överdriva": "exaggerate"},
    "art_19_s030": {"grönländska": "Greenlandic"},
    "art_19_s031": {"namn": "name"},
    "art_19_s032": {"döpa": "name", "få tillbaka": "get hope back"},
    "art_19_s033": {"snöboll": "snowball", "apelsinträd": "orange tree"},
    "art_19_s034": {"få problem": "getting into trouble"}
}

with open(art_19_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for sentence in data.get("sentences", []):
    s_id = sentence.get("sentence_id")
    en_text = sentence.get("en", "")
    for tw in sentence.get("target_words", []):
        word = tw.get("word_in_sentence")
        if s_id in mapping and word in mapping[s_id]:
            new_en = mapping[s_id][word]
            if new_en in en_text:
                tw["contextual_en"] = new_en
            else:
                print(f"Warning: {new_en} not in {en_text}")

with open(art_19_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)
    f.write('\n')

# Now strip fields for article_19.json
for sentence in data.get("sentences", []):
    if "en" in sentence:
        del sentence["en"]
    for tw in sentence.get("target_words", []):
        if "contextual_en" in tw:
            del tw["contextual_en"]
    for sw in sentence.get("secondary_words", []):
        if "contextual_en" in sw:
            del sw["contextual_en"]

with open(article_19_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)
    f.write('\n')

print("Done")
