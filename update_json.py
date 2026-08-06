import json
import os

def update_article(file_path, secondary_words_map):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    sentences = data.get('sentences', [])
    for i, sentence in enumerate(sentences):
        if i in secondary_words_map:
            words = secondary_words_map[i]
            # avoid duplicates with target words
            target_words_lower = [tw.get('word_in_sentence', '').lower() for tw in sentence.get('target_words', [])]
            for w in words:
                if w['word_in_sentence'].lower() not in target_words_lower:
                    sentence['secondary_words'].append(w)
                    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Updated {file_path}")

art_04_map = {
    0: [{"word_in_sentence": "vän", "base_form": "vän", "contextual_en": "friend"}, {"word_in_sentence": "liten", "base_form": "liten", "contextual_en": "small"}, {"word_in_sentence": "resa", "base_form": "resa", "contextual_en": "travel"}],
    1: [{"word_in_sentence": "vanliga", "base_form": "vanlig", "contextual_en": "usual"}, {"word_in_sentence": "eftersom", "base_form": "eftersom", "contextual_en": "because"}, {"word_in_sentence": "förändring", "base_form": "förändring", "contextual_en": "change"}],
    2: [{"word_in_sentence": "gånger", "base_form": "gång", "contextual_en": "times"}, {"word_in_sentence": "dags", "base_form": "dags", "contextual_en": "time"}, {"word_in_sentence": "ny", "base_form": "ny", "contextual_en": "new"}],
    3: [{"word_in_sentence": "ensam", "base_form": "ensam", "contextual_en": "lonely"}, {"word_in_sentence": "ofta", "base_form": "ofta", "contextual_en": "often"}, {"word_in_sentence": "resor", "base_form": "resa", "contextual_en": "travels"}],
    4: [{"word_in_sentence": "uppleva", "base_form": "uppleva", "contextual_en": "experience"}, {"word_in_sentence": "utsikt", "base_form": "utsikt", "contextual_en": "view"}, {"word_in_sentence": "gammal", "base_form": "gammal", "contextual_en": "old"}],
    6: [{"word_in_sentence": "verkligen", "base_form": "verkligen", "contextual_en": "really"}, {"word_in_sentence": "frågade", "base_form": "fråga", "contextual_en": "asked"}],
    7: [{"word_in_sentence": "nickade", "base_form": "nicka", "contextual_en": "nodded"}],
    8: [{"word_in_sentence": "flyg", "base_form": "flyg", "contextual_en": "flight"}, {"word_in_sentence": "sedan", "base_form": "sedan", "contextual_en": "then"}],
    9: [{"word_in_sentence": "hyra", "base_form": "hyra", "contextual_en": "rent"}, {"word_in_sentence": "kusten", "base_form": "kust", "contextual_en": "coast"}, {"word_in_sentence": "åka", "base_form": "åka", "contextual_en": "travel"}],
    10: [{"word_in_sentence": "Blunda", "base_form": "blunda", "contextual_en": "close eyes"}, {"word_in_sentence": "lyssnade", "base_form": "lyssna", "contextual_en": "listened"}, {"word_in_sentence": "lokal", "base_form": "lokal", "contextual_en": "local"}],
    11: [{"word_in_sentence": "äntligen", "base_form": "äntligen", "contextual_en": "finally"}, {"word_in_sentence": "framme", "base_form": "framme", "contextual_en": "arrived"}, {"word_in_sentence": "bestämde", "base_form": "bestämma", "contextual_en": "decided"}],
    12: [{"word_in_sentence": "måste", "base_form": "måste", "contextual_en": "must"}, {"word_in_sentence": "trevlig", "base_form": "trevlig", "contextual_en": "nice"}],
    13: [{"word_in_sentence": "fanns", "base_form": "finnas", "contextual_en": "were"}, {"word_in_sentence": "sorters", "base_form": "sort", "contextual_en": "sorts of"}, {"word_in_sentence": "båtar", "base_form": "båt", "contextual_en": "boats"}],
    14: [{"word_in_sentence": "lät", "base_form": "låta", "contextual_en": "let"}, {"word_in_sentence": "vattnet", "base_form": "vatten", "contextual_en": "water"}],
    15: [{"word_in_sentence": "valde", "base_form": "välja", "contextual_en": "chose"}, {"word_in_sentence": "strömmen", "base_form": "ström", "contextual_en": "flow"}, {"word_in_sentence": "slappna av", "base_form": "slappna av", "contextual_en": "relax"}],
    16: [{"word_in_sentence": "barn", "base_form": "barn", "contextual_en": "children"}, {"word_in_sentence": "stranden", "base_form": "strand", "contextual_en": "beach"}, {"word_in_sentence": "hund", "base_form": "hund", "contextual_en": "dog"}],
    17: [{"word_in_sentence": "kvällen", "base_form": "kväll", "contextual_en": "evening"}, {"word_in_sentence": "tänkte", "base_form": "tänka", "contextual_en": "thought"}, {"word_in_sentence": "gamla", "base_form": "gammal", "contextual_en": "old"}],
    18: [{"word_in_sentence": "äldre", "base_form": "äldre", "contextual_en": "older"}, {"word_in_sentence": "stenar", "base_form": "sten", "contextual_en": "stones"}, {"word_in_sentence": "världen", "base_form": "värld", "contextual_en": "world"}],
    19: [{"word_in_sentence": "Sök", "base_form": "söka", "contextual_en": "search"}, {"word_in_sentence": "själv", "base_form": "själv", "contextual_en": "yourself"}],
    20: [{"word_in_sentence": "verkade", "base_form": "verka", "contextual_en": "seemed"}, {"word_in_sentence": "väldigt", "base_form": "väldigt", "contextual_en": "very"}, {"word_in_sentence": "kändes", "base_form": "kännas", "contextual_en": "felt"}],
    21: [{"word_in_sentence": "semester", "base_form": "semester", "contextual_en": "vacation"}, {"word_in_sentence": "underbar", "base_form": "underbar", "contextual_en": "wonderful"}, {"word_in_sentence": "tid", "base_form": "tid", "contextual_en": "time"}],
    22: [{"word_in_sentence": "alltid", "base_form": "alltid", "contextual_en": "always"}, {"word_in_sentence": "lite", "base_form": "lite", "contextual_en": "a little"}],
    23: [{"word_in_sentence": "aldrig", "base_form": "aldrig", "contextual_en": "never"}, {"word_in_sentence": "tråkigt", "base_form": "tråkig", "contextual_en": "boring"}],
    24: [{"word_in_sentence": "hoppas", "base_form": "hoppas", "contextual_en": "hope"}, {"word_in_sentence": "göra", "base_form": "göra", "contextual_en": "make"}],
    25: [{"word_in_sentence": "synd", "base_form": "synd", "contextual_en": "shame"}, {"word_in_sentence": "lycklig", "base_form": "lycklig", "contextual_en": "happy"}, {"word_in_sentence": "havet", "base_form": "hav", "contextual_en": "sea"}]
}

art_05_map = {
    0: [{"word_in_sentence": "talar", "base_form": "tala", "contextual_en": "speak"}, {"word_in_sentence": "många", "base_form": "många", "contextual_en": "many"}, {"word_in_sentence": "bra", "base_form": "bra", "contextual_en": "good"}],
    1: [{"word_in_sentence": "tänkte", "base_form": "tänka", "contextual_en": "thought"}, {"word_in_sentence": "bli", "base_form": "bli", "contextual_en": "become"}],
    2: [{"word_in_sentence": "ändrades", "base_form": "ändras", "contextual_en": "changed"}],
    3: [{"word_in_sentence": "vän", "base_form": "vän", "contextual_en": "friend"}],
    4: [{"word_in_sentence": "berättade", "base_form": "berätta", "contextual_en": "told"}, {"word_in_sentence": "mörk", "base_form": "mörk", "contextual_en": "dark"}],
    5: [{"word_in_sentence": "välja", "base_form": "välja", "contextual_en": "choose"}, {"word_in_sentence": "sitta", "base_form": "sitta", "contextual_en": "sit"}, {"word_in_sentence": "kontor", "base_form": "kontor", "contextual_en": "office"}],
    6: [{"word_in_sentence": "vanlig", "base_form": "vanlig", "contextual_en": "regular"}, {"word_in_sentence": "ofta", "base_form": "ofta", "contextual_en": "often"}],
    7: [{"word_in_sentence": "Ibland", "base_form": "ibland", "contextual_en": "sometimes"}, {"word_in_sentence": "miljö", "base_form": "miljö", "contextual_en": "environment"}, {"word_in_sentence": "tuff", "base_form": "tuff", "contextual_en": "tough"}],
    8: [{"word_in_sentence": "gillar", "base_form": "gilla", "contextual_en": "like"}, {"word_in_sentence": "uppgifter", "base_form": "uppgift", "contextual_en": "tasks"}, {"word_in_sentence": "alltid", "base_form": "alltid", "contextual_en": "always"}],
    9: [{"word_in_sentence": "vänner", "base_form": "vän", "contextual_en": "friends"}],
    10: [{"word_in_sentence": "samma", "base_form": "samma", "contextual_en": "same"}, {"word_in_sentence": "viktigt", "base_form": "viktig", "contextual_en": "important"}],
    11: [{"word_in_sentence": "hjälper", "base_form": "hjälpa", "contextual_en": "help"}, {"word_in_sentence": "kurser", "base_form": "kurs", "contextual_en": "courses"}, {"word_in_sentence": "rimlig", "base_form": "rimlig", "contextual_en": "reasonable"}],
    12: [{"word_in_sentence": "extrem", "base_form": "extrem", "contextual_en": "extreme"}],
    13: [{"word_in_sentence": "chef", "base_form": "chef", "contextual_en": "boss"}, {"word_in_sentence": "ibland", "base_form": "ibland", "contextual_en": "sometimes"}],
    14: [{"word_in_sentence": "besöker", "base_form": "besöka", "contextual_en": "visits"}, {"word_in_sentence": "göra", "base_form": "göra", "contextual_en": "do"}],
    15: [{"word_in_sentence": "grupp", "base_form": "grupp", "contextual_en": "group"}, {"word_in_sentence": "försöker", "base_form": "försöka", "contextual_en": "try"}, {"word_in_sentence": "skapa", "base_form": "skapa", "contextual_en": "create"}],
    16: [{"word_in_sentence": "lätt", "base_form": "lätt", "contextual_en": "easy"}, {"word_in_sentence": "bransch", "base_form": "bransch", "contextual_en": "industry"}],
    17: [{"word_in_sentence": "jämfört", "base_form": "jämföra", "contextual_en": "compared"}, {"word_in_sentence": "tunga", "base_form": "tung", "contextual_en": "heavy"}],
    18: [{"word_in_sentence": "betalar", "base_form": "betala", "contextual_en": "pay"}, {"word_in_sentence": "allt", "base_form": "allt", "contextual_en": "everything"}],
    19: [{"word_in_sentence": "räcker", "base_form": "räcka", "contextual_en": "enough"}, {"word_in_sentence": "oftast", "base_form": "oftast", "contextual_en": "usually"}],
    20: [{"word_in_sentence": "maskiner", "base_form": "maskin", "contextual_en": "machines"}, {"word_in_sentence": "pratade", "base_form": "prata", "contextual_en": "talked"}],
    21: [{"word_in_sentence": "undvika", "base_form": "undvika", "contextual_en": "avoid"}],
    22: [{"word_in_sentence": "njuta", "base_form": "njuta", "contextual_en": "enjoy"}, {"word_in_sentence": "helg", "base_form": "helg", "contextual_en": "weekend"}],
    23: [{"word_in_sentence": "skönt", "base_form": "skön", "contextual_en": "nice"}, {"word_in_sentence": "bort", "base_form": "bort", "contextual_en": "away"}],
    24: [{"word_in_sentence": "vila", "base_form": "vila", "contextual_en": "rest"}, {"word_in_sentence": "dags", "base_form": "dags", "contextual_en": "time"}],
    25: [{"word_in_sentence": "tungt", "base_form": "tung", "contextual_en": "exhausting"}, {"word_in_sentence": "hem", "base_form": "hem", "contextual_en": "home"}],
    26: [{"word_in_sentence": "glad", "base_form": "glad", "contextual_en": "happy"}, {"word_in_sentence": "hoppas", "base_form": "hoppas", "contextual_en": "hope"}, {"word_in_sentence": "framöver", "base_form": "framöver", "contextual_en": "in the future"}],
    27: [{"word_in_sentence": "familj", "base_form": "familj", "contextual_en": "family"}, {"word_in_sentence": "roligt", "base_form": "rolig", "contextual_en": "fun"}, {"word_in_sentence": "stress", "base_form": "stress", "contextual_en": "stress"}],
    28: [{"word_in_sentence": "hörde", "base_form": "höra", "contextual_en": "heard"}, {"word_in_sentence": "älska", "base_form": "älska", "contextual_en": "love"}]
}

art_06_map = {
    0: [{"word_in_sentence": "börjar", "base_form": "börja", "contextual_en": "begins"}, {"word_in_sentence": "första", "base_form": "första", "contextual_en": "first"}, {"word_in_sentence": "gången", "base_form": "gång", "contextual_en": "time"}],
    1: [{"word_in_sentence": "chef", "base_form": "chef", "contextual_en": "boss"}],
    2: [{"word_in_sentence": "vanlig", "base_form": "vanlig", "contextual_en": "regular"}, {"word_in_sentence": "staden", "base_form": "stad", "contextual_en": "city"}, {"word_in_sentence": "föräldrar", "base_form": "förälder", "contextual_en": "parents"}],
    3: [{"word_in_sentence": "ville", "base_form": "vilja", "contextual_en": "wanted"}],
    4: [{"word_in_sentence": "började", "base_form": "börja", "contextual_en": "started"}],
    5: [{"word_in_sentence": "permanent", "base_form": "permanent", "contextual_en": "permanently"}, {"word_in_sentence": "sommaren", "base_form": "sommar", "contextual_en": "summer"}],
    6: [{"word_in_sentence": "år", "base_form": "år", "contextual_en": "years"}, {"word_in_sentence": "jobbat", "base_form": "jobba", "contextual_en": "worked"}],
    7: [{"word_in_sentence": "nyss", "base_form": "nyss", "contextual_en": "newly"}],
    8: [{"word_in_sentence": "stort", "base_form": "stor", "contextual_en": "large"}],
    9: [{"word_in_sentence": "gott", "base_form": "god", "contextual_en": "good"}],
    10: [{"word_in_sentence": "annan", "base_form": "annan", "contextual_en": "other"}, {"word_in_sentence": "kunde", "base_form": "kunna", "contextual_en": "could"}],
    11: [{"word_in_sentence": "världen", "base_form": "värld", "contextual_en": "world"}, {"word_in_sentence": "ändå", "base_form": "ändå", "contextual_en": "nonetheless"}, {"word_in_sentence": "framgångsrika", "base_form": "framgångsrik", "contextual_en": "successful"}],
    12: [{"word_in_sentence": "utländsk", "base_form": "utländsk", "contextual_en": "foreign"}, {"word_in_sentence": "partner", "base_form": "partner", "contextual_en": "partner"}, {"word_in_sentence": "behövde", "base_form": "behöva", "contextual_en": "needed"}],
    13: [{"word_in_sentence": "tvungna", "base_form": "tvungen", "contextual_en": "forced"}, {"word_in_sentence": "tydligt", "base_form": "tydlig", "contextual_en": "clear"}],
    14: [{"word_in_sentence": "tog över", "base_form": "ta över", "contextual_en": "took over"}, {"word_in_sentence": "problem", "base_form": "problem", "contextual_en": "problems"}],
    15: [{"word_in_sentence": "regler", "base_form": "regel", "contextual_en": "rules"}, {"word_in_sentence": "saknade", "base_form": "sakna", "contextual_en": "lacked"}, {"word_in_sentence": "mening", "base_form": "mening", "contextual_en": "sense"}],
    16: [{"word_in_sentence": "sent", "base_form": "sen", "contextual_en": "late"}, {"word_in_sentence": "glömde", "base_form": "glömma", "contextual_en": "forgot"}, {"word_in_sentence": "beställa", "base_form": "beställa", "contextual_en": "order"}],
    17: [{"word_in_sentence": "viktigt", "base_form": "viktig", "contextual_en": "important"}],
    18: [{"word_in_sentence": "Annars", "base_form": "annars", "contextual_en": "otherwise"}, {"word_in_sentence": "folk", "base_form": "folk", "contextual_en": "people"}],
    19: [{"word_in_sentence": "dröm", "base_form": "dröm", "contextual_en": "dream"}],
    20: [{"word_in_sentence": "talade", "base_form": "tala", "contextual_en": "talked"}, {"word_in_sentence": "metoder", "base_form": "metod", "contextual_en": "methods"}],
    21: [{"word_in_sentence": "kollega", "base_form": "kollega", "contextual_en": "colleague"}],
    22: [{"word_in_sentence": "måste", "base_form": "måste", "contextual_en": "have to"}],
    23: [{"word_in_sentence": "nya", "base_form": "ny", "contextual_en": "new"}, {"word_in_sentence": "under", "base_form": "under", "contextual_en": "during"}],
    24: [{"word_in_sentence": "mycket", "base_form": "mycket", "contextual_en": "a lot of"}],
    25: [{"word_in_sentence": "anställda", "base_form": "anställd", "contextual_en": "employees"}, {"word_in_sentence": "följ", "base_form": "följa", "contextual_en": "follow"}, {"word_in_sentence": "noga", "base_form": "noga", "contextual_en": "carefully"}],
    26: [{"word_in_sentence": "bad", "base_form": "be", "contextual_en": "asked"}, {"word_in_sentence": "lånar", "base_form": "låna", "contextual_en": "borrow"}],
    27: [{"word_in_sentence": "skrev", "base_form": "skriva", "contextual_en": "wrote"}, {"word_in_sentence": "mejl", "base_form": "mejl", "contextual_en": "email"}, {"word_in_sentence": "tid", "base_form": "tid", "contextual_en": "time"}],
    28: [{"word_in_sentence": "information", "base_form": "information", "contextual_en": "information"}, {"word_in_sentence": "mötet", "base_form": "möte", "contextual_en": "meeting"}],
    29: [{"word_in_sentence": "rummet", "base_form": "rum", "contextual_en": "room"}]
}

art_07_map = {
    0: [{"word_in_sentence": "vecka", "base_form": "vecka", "contextual_en": "week"}, {"word_in_sentence": "kontoret", "base_form": "kontor", "contextual_en": "office"}, {"word_in_sentence": "läsa", "base_form": "läsa", "contextual_en": "read"}],
    1: [{"word_in_sentence": "nytt", "base_form": "ny", "contextual_en": "new"}],
    2: [{"word_in_sentence": "bredvid", "base_form": "bredvid", "contextual_en": "next to"}],
    3: [{"word_in_sentence": "staden", "base_form": "stad", "contextual_en": "city"}],
    4: [{"word_in_sentence": "planerade", "base_form": "planera", "contextual_en": "planned"}],
    5: [{"word_in_sentence": "hoppades", "base_form": "hoppas", "contextual_en": "hoped"}],
    6: [{"word_in_sentence": "behövde", "base_form": "behöva", "contextual_en": "needed"}],
    7: [{"word_in_sentence": "hjälpa till", "base_form": "hjälpa till", "contextual_en": "help"}],
    8: [{"word_in_sentence": "försöka", "base_form": "försöka", "contextual_en": "try"}],
    9: [{"word_in_sentence": "min", "base_form": "min", "contextual_en": "my"}],
    10: [{"word_in_sentence": "viktigt", "base_form": "viktig", "contextual_en": "important"}],
    11: [{"word_in_sentence": "noga", "base_form": "noga", "contextual_en": "careful"}, {"word_in_sentence": "rätt", "base_form": "rätt", "contextual_en": "right"}],
    12: [{"word_in_sentence": "skrivit", "base_form": "skriva", "contextual_en": "written"}, {"word_in_sentence": "tavla", "base_form": "tavla", "contextual_en": "board"}, {"word_in_sentence": "skärmen", "base_form": "skärm", "contextual_en": "screen"}],
    13: [{"word_in_sentence": "använda", "base_form": "använda", "contextual_en": "use"}],
    14: [{"word_in_sentence": "framtiden", "base_form": "framtid", "contextual_en": "future"}],
    15: [{"word_in_sentence": "mer", "base_form": "mer", "contextual_en": "more"}],
    16: [{"word_in_sentence": "säkerhet", "base_form": "säkerhet", "contextual_en": "safety"}, {"word_in_sentence": "varje", "base_form": "varje", "contextual_en": "every"}],
    17: [{"word_in_sentence": "behöver", "base_form": "behöva", "contextual_en": "need"}, {"word_in_sentence": "avtal", "base_form": "avtal", "contextual_en": "contracts"}],
    18: [{"word_in_sentence": "tid", "base_form": "tid", "contextual_en": "time"}],
    19: [{"word_in_sentence": "arbetet", "base_form": "arbete", "contextual_en": "work"}, {"word_in_sentence": "månad", "base_form": "månad", "contextual_en": "month"}],
    20: [{"word_in_sentence": "säkerhetsfrågor", "base_form": "säkerhetsfråga", "contextual_en": "security issues"}],
    21: [{"word_in_sentence": "anställa", "base_form": "anställa", "contextual_en": "hiring"}, {"word_in_sentence": "kantinen", "base_form": "kantin", "contextual_en": "canteen"}],
    22: [{"word_in_sentence": "just nu", "base_form": "just nu", "contextual_en": "right now"}],
    23: [{"word_in_sentence": "chans", "base_form": "chans", "contextual_en": "chance"}],
    24: [{"word_in_sentence": "klubben", "base_form": "klubb", "contextual_en": "club"}, {"word_in_sentence": "plats", "base_form": "plats", "contextual_en": "place"}, {"word_in_sentence": "nöjd", "base_form": "nöjd", "contextual_en": "satisfied"}]
}

base_dir = "./course/sfid/phase2/articles_translated"

update_article(os.path.join(base_dir, "art_04.json"), art_04_map)
update_article(os.path.join(base_dir, "art_05.json"), art_05_map)
update_article(os.path.join(base_dir, "art_06.json"), art_06_map)
update_article(os.path.join(base_dir, "art_07.json"), art_07_map)
