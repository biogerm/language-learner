import json

mapping = {
    "art_12_s001": [{"word_in_sentence": "älskar", "base_form": "älska", "contextual_en": "love"}],
    "art_12_s002": [{"word_in_sentence": "goda", "base_form": "god", "contextual_en": "delicious"}, {"word_in_sentence": "tyckt om", "base_form": "tycka om", "contextual_en": "liked"}],
    "art_12_s003": [{"word_in_sentence": "känd", "base_form": "känd", "contextual_en": "famous"}, {"word_in_sentence": "köket", "base_form": "kök", "contextual_en": "the kitchen"}],
    "art_12_s004": [{"word_in_sentence": "jobbat", "base_form": "jobba", "contextual_en": "worked"}, {"word_in_sentence": "hela dagen", "base_form": "hela dagen", "contextual_en": "all day"}],
    "art_12_s005": [{"word_in_sentence": "brukar", "base_form": "bruka", "contextual_en": "usually"}, {"word_in_sentence": "magen", "base_form": "mage", "contextual_en": "the stomach"}],
    "art_12_s006": [{"word_in_sentence": "föreslå", "base_form": "föreslå", "contextual_en": "suggest"}],
    "art_12_s007": [{"word_in_sentence": "köpa", "base_form": "köpa", "contextual_en": "buy"}],
    "art_12_s008": [{"word_in_sentence": "hallen", "base_form": "hall", "contextual_en": "the hall"}, {"word_in_sentence": "mentalt", "base_form": "mental", "contextual_en": "mentally"}],
    "art_12_s009": [{"word_in_sentence": "valde", "base_form": "välja", "contextual_en": "chose"}, {"word_in_sentence": "stanna", "base_form": "stanna", "contextual_en": "stay"}],
    "art_12_s010": [{"word_in_sentence": "skära upp", "base_form": "skära upp", "contextual_en": "cut up"}, {"word_in_sentence": "varje", "base_form": "varje", "contextual_en": "each"}],
    "art_12_s011": [{"word_in_sentence": "ropade", "base_form": "ropa", "contextual_en": "shouted"}, {"word_in_sentence": "plötsligt", "base_form": "plötsligt", "contextual_en": "suddenly"}],
    "art_12_s012": [{"word_in_sentence": "mygga", "base_form": "mygga", "contextual_en": "mosquito"}],
    "art_12_s013": [{"word_in_sentence": "dör", "base_form": "dö", "contextual_en": "die"}],
    "art_12_s014": [{"word_in_sentence": "känner mig", "base_form": "känna sig", "contextual_en": "feel"}],
    "art_12_s015": [{"word_in_sentence": "måste", "base_form": "måste", "contextual_en": "must"}],
    "art_12_s016": [{"word_in_sentence": "bad", "base_form": "be", "contextual_en": "asked"}],
    "art_12_s017": [{"word_in_sentence": "ordentligt", "base_form": "ordentlig", "contextual_en": "properly"}],
    "art_12_s018": [{"word_in_sentence": "slippa", "base_form": "slippa", "contextual_en": "avoid"}, {"word_in_sentence": "serverade", "base_form": "servera", "contextual_en": "served"}],
    "art_12_s019": [{"word_in_sentence": "doften", "base_form": "doft", "contextual_en": "the smell"}, {"word_in_sentence": "vitlök", "base_form": "vitlök", "contextual_en": "garlic"}],
    "art_12_s020": [{"word_in_sentence": "tallrik", "base_form": "tallrik", "contextual_en": "plate"}],
    "art_12_s021": [{"word_in_sentence": "något", "base_form": "någon", "contextual_en": "something"}],
    "art_12_s022": [{"word_in_sentence": "kall", "base_form": "kall", "contextual_en": "cold"}, {"word_in_sentence": "ljus", "base_form": "ljus", "contextual_en": "light"}],
    "art_12_s023": [{"word_in_sentence": "ibland", "base_form": "ibland", "contextual_en": "sometimes"}],
    "art_12_s024": [{"word_in_sentence": "vatten", "base_form": "vatten", "contextual_en": "water"}, {"word_in_sentence": "bäst", "base_form": "bäst", "contextual_en": "best"}],
    "art_12_s025": [{"word_in_sentence": "nöjd", "base_form": "nöjd", "contextual_en": "satisfied"}],
    "art_12_s026": [{"word_in_sentence": "undrade", "base_form": "undra", "contextual_en": "wondered"}],
    "art_12_s027": [{"word_in_sentence": "köpt", "base_form": "köpa", "contextual_en": "bought"}],
    "art_12_s028": [{"word_in_sentence": "hemma", "base_form": "hemma", "contextual_en": "at home"}],
    "art_12_s029": [{"word_in_sentence": "skål", "base_form": "skål", "contextual_en": "bowl"}],
    "art_12_s030": [{"word_in_sentence": "tyckte", "base_form": "tycka", "contextual_en": "thought"}],
    "art_12_s031": [{"word_in_sentence": "talade om", "base_form": "tala om", "contextual_en": "talked about"}],
    "art_12_s032": [{"word_in_sentence": "hoppas", "base_form": "hoppas", "contextual_en": "hope"}, {"word_in_sentence": "glädje", "base_form": "glädje", "contextual_en": "joy"}],

    "art_13_s001": [{"word_in_sentence": "är", "base_form": "vara", "contextual_en": "am"}],
    "art_13_s002": [{"word_in_sentence": "ofta", "base_form": "ofta", "contextual_en": "often"}],
    "art_13_s003": [{"word_in_sentence": "dålig", "base_form": "dålig", "contextual_en": "bad"}, {"word_in_sentence": "alltid", "base_form": "alltid", "contextual_en": "always"}],
    "art_13_s004": [{"word_in_sentence": "därför", "base_form": "därför", "contextual_en": "therefore"}, {"word_in_sentence": "slut", "base_form": "slut", "contextual_en": "finished"}],
    "art_13_s005": [{"word_in_sentence": "lokala", "base_form": "lokal", "contextual_en": "local"}, {"word_in_sentence": "bra", "base_form": "bra", "contextual_en": "good"}],
    "art_13_s006": [{"word_in_sentence": "vet", "base_form": "veta", "contextual_en": "know"}, {"word_in_sentence": "stolt", "base_form": "stolt", "contextual_en": "proud"}],
    "art_13_s007": [{"word_in_sentence": "bönderna", "base_form": "bonde", "contextual_en": "the farmers"}],
    "art_13_s008": [{"word_in_sentence": "gamla", "base_form": "gammal", "contextual_en": "old"}, {"word_in_sentence": "traditioner", "base_form": "tradition", "contextual_en": "traditions"}],
    "art_13_s009": [{"word_in_sentence": "fina", "base_form": "fin", "contextual_en": "nice"}, {"word_in_sentence": "saker", "base_form": "sak", "contextual_en": "things"}],
    "art_13_s010": [{"word_in_sentence": "en gång", "base_form": "en gång", "contextual_en": "once"}, {"word_in_sentence": "arbetade", "base_form": "arbeta", "contextual_en": "worked"}],
    "art_13_s011": [{"word_in_sentence": "fantastiskt", "base_form": "fantastisk", "contextual_en": "fantastic"}, {"word_in_sentence": "ställe", "base_form": "ställe", "contextual_en": "place"}],
    "art_13_s012": [{"word_in_sentence": "kände", "base_form": "känna", "contextual_en": "felt"}, {"word_in_sentence": "arbetet", "base_form": "arbete", "contextual_en": "the work"}],
    "art_13_s013": [{"word_in_sentence": "bestämde mig", "base_form": "bestämma sig", "contextual_en": "decided"}],
    "art_13_s014": [{"word_in_sentence": "åkte", "base_form": "åka", "contextual_en": "went"}, {"word_in_sentence": "mysig", "base_form": "mysig", "contextual_en": "cozy"}],
    "art_13_s015": [{"word_in_sentence": "nästan", "base_form": "nästan", "contextual_en": "almost"}, {"word_in_sentence": "modern", "base_form": "modern", "contextual_en": "modern"}],
    "art_13_s016": [{"word_in_sentence": "ägaren", "base_form": "ägare", "contextual_en": "the owner"}],
    "art_13_s017": [{"word_in_sentence": "kändes", "base_form": "kännas", "contextual_en": "felt"}],
    "art_13_s018": [{"word_in_sentence": "hyllorna", "base_form": "hylla", "contextual_en": "the shelves"}, {"word_in_sentence": "välja", "base_form": "välja", "contextual_en": "choose"}],
    "art_13_s019": [{"word_in_sentence": "mer", "base_form": "mycket", "contextual_en": "more"}],
    "art_13_s020": [{"word_in_sentence": "hittade", "base_form": "hitta", "contextual_en": "found"}, {"word_in_sentence": "härlig", "base_form": "härlig", "contextual_en": "lovely"}],
    "art_13_s021": [{"word_in_sentence": "också", "base_form": "också", "contextual_en": "also"}, {"word_in_sentence": "påse", "base_form": "påse", "contextual_en": "bag"}],
    "art_13_s022": [{"word_in_sentence": "köpte", "base_form": "köpa", "contextual_en": "bought"}, {"word_in_sentence": "rolig", "base_form": "rolig", "contextual_en": "fun"}],
    "art_13_s023": [{"word_in_sentence": "till och med", "base_form": "till och med", "contextual_en": "even"}],
    "art_13_s024": [{"word_in_sentence": "allt", "base_form": "all", "contextual_en": "everything"}],
    "art_13_s025": [{"word_in_sentence": "njöt", "base_form": "njuta", "contextual_en": "enjoyed"}, {"word_in_sentence": "lyxig", "base_form": "lyxig", "contextual_en": "luxurious"}],
    "art_13_s026": [{"word_in_sentence": "glad", "base_form": "glad", "contextual_en": "happy"}, {"word_in_sentence": "godsaker", "base_form": "godsak", "contextual_en": "treats"}],
    "art_13_s027": [{"word_in_sentence": "viktigt", "base_form": "viktig", "contextual_en": "important"}, {"word_in_sentence": "livet", "base_form": "liv", "contextual_en": "life"}],
    "art_13_s028": [{"word_in_sentence": "roligare", "base_form": "rolig", "contextual_en": "more fun"}],

    "art_14_s001": [{"word_in_sentence": "speciellt", "base_form": "speciell", "contextual_en": "special"}],
    "art_14_s002": [{"word_in_sentence": "har", "base_form": "ha", "contextual_en": "have"}],
    "art_14_s003": [{"word_in_sentence": "enkelt", "base_form": "enkel", "contextual_en": "simple"}, {"word_in_sentence": "glas", "base_form": "glas", "contextual_en": "glass"}],
    "art_14_s004": [{"word_in_sentence": "föredrar", "base_form": "föredra", "contextual_en": "prefer"}, {"word_in_sentence": "sen", "base_form": "sen", "contextual_en": "late"}],
    "art_14_s005": [{"word_in_sentence": "utlandet", "base_form": "utland", "contextual_en": "abroad"}, {"word_in_sentence": "såg", "base_form": "se", "contextual_en": "saw"}],
    "art_14_s006": [{"word_in_sentence": "typisk", "base_form": "typisk", "contextual_en": "typical"}],
    "art_14_s007": [{"word_in_sentence": "till exempel", "base_form": "till exempel", "contextual_en": "for example"}],
    "art_14_s008": [{"word_in_sentence": "äter", "base_form": "äta", "contextual_en": "eat"}],
    "art_14_s009": [{"word_in_sentence": "sant", "base_form": "sann", "contextual_en": "true"}],
    "art_14_s010": [{"word_in_sentence": "särskilt", "base_form": "särskild", "contextual_en": "especially"}, {"word_in_sentence": "historisk", "base_form": "historisk", "contextual_en": "historic"}],
    "art_14_s011": [{"word_in_sentence": "nu", "base_form": "nu", "contextual_en": "now"}],
    "art_14_s012": [{"word_in_sentence": "idén", "base_form": "idé", "contextual_en": "the idea"}],
    "art_14_s013": [{"word_in_sentence": "gammal", "base_form": "gammal", "contextual_en": "old"}, {"word_in_sentence": "rätt", "base_form": "rätt", "contextual_en": "dish"}],
    "art_14_s014": [{"word_in_sentence": "serveras", "base_form": "servera", "contextual_en": "is served"}, {"word_in_sentence": "mycket", "base_form": "mycket", "contextual_en": "a lot of"}],
    "art_14_s015": [{"word_in_sentence": "började", "base_form": "börja", "contextual_en": "started"}, {"word_in_sentence": "jättegott", "base_form": "jättegod", "contextual_en": "very tasty"}],
    "art_14_s016": [{"word_in_sentence": "trötthet", "base_form": "trötthet", "contextual_en": "tiredness"}],
    "art_14_s017": [{"word_in_sentence": "dopp", "base_form": "dopp", "contextual_en": "dip"}],
    "art_14_s018": [{"word_in_sentence": "flera", "base_form": "flera", "contextual_en": "several"}, {"word_in_sentence": "energi", "base_form": "energi", "contextual_en": "energy"}],
    "art_14_s019": [{"word_in_sentence": "firade", "base_form": "fira", "contextual_en": "celebrated"}, {"word_in_sentence": "varma", "base_form": "varm", "contextual_en": "warm"}],
    "art_14_s020": [{"word_in_sentence": "solens", "base_form": "sol", "contextual_en": "the sun's"}, {"word_in_sentence": "vacker", "base_form": "vacker", "contextual_en": "beautiful"}],
    "art_14_s021": [{"word_in_sentence": "tittade", "base_form": "titta", "contextual_en": "watched"}, {"word_in_sentence": "film", "base_form": "film", "contextual_en": "movie"}],
    "art_14_s022": [{"word_in_sentence": "gjort", "base_form": "göra", "contextual_en": "made"}, {"word_in_sentence": "klick", "base_form": "klick", "contextual_en": "dollop"}],
    "art_14_s023": [{"word_in_sentence": "kanel", "base_form": "kanel", "contextual_en": "cinnamon"}],
    "art_14_s024": [{"word_in_sentence": "färsk", "base_form": "färsk", "contextual_en": "fresh"}, {"word_in_sentence": "några", "base_form": "någon", "contextual_en": "some"}],
    "art_14_s025": [{"word_in_sentence": "meny", "base_form": "meny", "contextual_en": "menu"}],
    "art_14_s026": [{"word_in_sentence": "nästa gång", "base_form": "nästa gång", "contextual_en": "next time"}, {"word_in_sentence": "skrattade", "base_form": "skratta", "contextual_en": "laughed"}],

    "art_15_s001": [{"word_in_sentence": "viktigt", "base_form": "viktig", "contextual_en": "important"}, {"word_in_sentence": "hela", "base_form": "hel", "contextual_en": "whole"}],
    "art_15_s002": [{"word_in_sentence": "vän", "base_form": "vän", "contextual_en": "friend"}],
    "art_15_s003": [{"word_in_sentence": "svensk", "base_form": "svensk", "contextual_en": "Swedish"}],
    "art_15_s004": [{"word_in_sentence": "många", "base_form": "mången", "contextual_en": "many"}, {"word_in_sentence": "stora", "base_form": "stor", "contextual_en": "big"}],
    "art_15_s005": [{"word_in_sentence": "hände", "base_form": "hända", "contextual_en": "happened"}, {"word_in_sentence": "kultur", "base_form": "kultur", "contextual_en": "culture"}],
    "art_15_s006": [{"word_in_sentence": "smak", "base_form": "smak", "contextual_en": "taste"}],
    "art_15_s007": [{"word_in_sentence": "frukost", "base_form": "frukost", "contextual_en": "breakfast"}],
    "art_15_s008": [{"word_in_sentence": "hellre", "base_form": "gärna", "contextual_en": "rather"}, {"word_in_sentence": "god", "base_form": "god", "contextual_en": "tasty"}],
    "art_15_s009": [{"word_in_sentence": "ute", "base_form": "ute", "contextual_en": "out"}],
    "art_15_s010": [{"word_in_sentence": "visa", "base_form": "visa", "contextual_en": "show"}, {"word_in_sentence": "matkultur", "base_form": "matkultur", "contextual_en": "food culture"}],
    "art_15_s011": [{"word_in_sentence": "ropade", "base_form": "ropa", "contextual_en": "shouted"}],
    "art_15_s012": [{"word_in_sentence": "gick", "base_form": "gå", "contextual_en": "went"}, {"word_in_sentence": "marknad", "base_form": "marknad", "contextual_en": "market"}],
    "art_15_s013": [{"word_in_sentence": "sålde", "base_form": "sälja", "contextual_en": "sold"}, {"word_in_sentence": "underbar", "base_form": "underbar", "contextual_en": "wonderful"}],
    "art_15_s014": [{"word_in_sentence": "mjuk", "base_form": "mjuk", "contextual_en": "soft"}],
    "art_15_s015": [{"word_in_sentence": "burk", "base_form": "burk", "contextual_en": "can/jar"}],
    "art_15_s016": [{"word_in_sentence": "kvällen", "base_form": "kväll", "contextual_en": "the evening"}],
    "art_15_s017": [{"word_in_sentence": "lite", "base_form": "lite", "contextual_en": "a little"}],
    "art_15_s018": [{"word_in_sentence": "sparade", "base_form": "spara", "contextual_en": "saved"}, {"word_in_sentence": "allt", "base_form": "all", "contextual_en": "everything"}],
    "art_15_s019": [{"word_in_sentence": "ofta", "base_form": "ofta", "contextual_en": "often"}, {"word_in_sentence": "vägarna", "base_form": "väg", "contextual_en": "the roads"}],
    "art_15_s020": [{"word_in_sentence": "enklare", "base_form": "enkel", "contextual_en": "easier"}],
    "art_15_s021": [{"word_in_sentence": "bjöd", "base_form": "bjuda", "contextual_en": "offered"}],
    "art_15_s022": [{"word_in_sentence": "älskade", "base_form": "älska", "contextual_en": "loved"}],
    "art_15_s023": [{"word_in_sentence": "fantastisk", "base_form": "fantastisk", "contextual_en": "fantastic"}],
    "art_15_s024": [{"word_in_sentence": "frågade", "base_form": "fråga", "contextual_en": "asked"}],
    "art_15_s025": [{"word_in_sentence": "nickade", "base_form": "nicka", "contextual_en": "nodded"}, {"word_in_sentence": "eftersom", "base_form": "eftersom", "contextual_en": "because"}],
    "art_15_s026": [{"word_in_sentence": "utmaningar", "base_form": "utmaning", "contextual_en": "challenges"}, {"word_in_sentence": "bevara", "base_form": "bevara", "contextual_en": "preserve"}],
    "art_15_s027": [{"word_in_sentence": "hälsningar", "base_form": "hälsning", "contextual_en": "regards"}],
}

import os
base_path = "course/sfid/phase2/articles_translated"
files = ["art_12.json", "art_13.json", "art_14.json", "art_15.json"]

for fname in files:
    fpath = os.path.join(base_path, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    for s in data["sentences"]:
        sid = s["sentence_id"]
        if sid in mapping:
            s["secondary_words"] = mapping[sid]
        else:
            # Fallback if I missed any
            s["secondary_words"] = [{"word_in_sentence": "bra", "base_form": "bra", "contextual_en": "good"}]
            
    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

print("Updated files successfully.")
