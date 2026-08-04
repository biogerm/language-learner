import json
import os

replacements = {
    0: [("hitta på rätt balans", "hitta rätt balans"), ("vi i genomsnitt spenderar", "spenderar vi i genomsnitt")],
    1: [("sätta på datorn", "starta datorn"), ("långt före vi bygger dem", "långt innan vi bygger dem")],
    2: [("biliotekarie", "bibliotekarie")],
    3: [("ferraribil", "sportbil"), ("turistnäring är stark", "turistnäringen är stark"), ("turisinformation", "turistinformation"), ("åka ur skogen", "åka ut ur skogen")],
    5: [("skogsindustri eller tung gruvindustri", "skogsindustrin eller den tunga gruvindustrin"), ("Komma hem", "komma hem"), ("när vi äntligen är ledig", "när vi äntligen är lediga")],
    6: [("livmedelsföretag", "livsmedelsföretag"), ("kontormaterial", "kontorsmaterial"), ("inte... förrän", "inte förrän"), ("I have a dream", "Jag har en dröm")],
    7: [("en fet lyxvara", "en dyr lyxvara"), ("prova/försöka", "försöka")],
    8: [("univerisitet", "universitet"), ("blåsa torr sitt hår", "föna håret")],
    9: [("orspråk", "ordspråk"), ("understuken", "understruken")],
    10: [("så många som möjligt timmar", "så många timmar som möjligt"), ("ordkunkskapsövning", "ordkunskapsövning"), ("asssimilation", "assimilation"), ("reflexiv pronomen", "reflexiva pronomen")],
    11: [("giantisk", "gigantisk"), ("summa språk", "mängd språk")],
    12: [("ntally", "mentalt")],
    14: [("idén var lite knäppt", "idén var lite knäpp"), ("några björnbär som verkade vara begravd", "några björnbär som verkade vara begravda")],
    15: [('"Okej då." sa jag', '"Okej då", sa jag')],
    16: [("ugnstekt", "ugnsstekt")],
    17: [("sällskpasdjur", "sällskapsdjur"), ("utfiskad på fisk", "tömd på fisk")],
    18: [("utlramodern", "ultramodern")],
    19: [("svarade jag bestämd", "svarade jag bestämt")],
    20: [("forkning", "forskning"), ("berg -och dalbana", "berg- och dalbana"), ("byggd av rent trä", "byggd i gediget trä")],
    21: [("En spanske turist", "En spansk turist"), ("himla vackert", "en suggestiv miljö")],
    22: [("motienera", "motionera"), ("lite... för sig", "på sitt eget sätt")],
    23: [("ska/skall", "ska"), (" även kallad doktor i vardagligt tal", ""), ("som kan indirekt påverka", "som indirekt kan påverka")],
    24: [("f.kr. Före Kristus", "f.Kr."), ("normala/vanliga", "det normala"), ("fylld med varm soppa", "fyllda med varm soppa")],
    25: [("(böjning: massmediet, massmedier, massmedierna)", ""), ("sammasatt", "sammansatt"), ("för att trygga sin framtid", "för att trygga vår framtid")],
    26: [("I kalla januari", "En kall januari"), ("rabies-smittad", "rabiessmittad"), ("giva", "ge")],
    27: [("alkis /alkoholist", "alkoholist"), ("alkis/alkoholist", "alkoholist"), ("fylle- misstag", "fyllemisstag"), ("viktigt genom att det hjälper", "viktigt eftersom det hjälper")],
    28: [("en form av dyr löparsko", "ett par dyra löparskor"), ("En otroligt hög prisnivå", "ett otroligt högt pris"), ("månaden/veckan", "veckan"), ("Det får ta så lång tid det behöver", "Det får ta den tid det behöver")],
    29: [("hålla i fångenskap min energi", "hålla min energi i fångenskap"), ("lik mig i smaken", "har liknande smak som jag")],
    30: [("Hoppas ni alla/du mår bra", "Hoppas ni alla mår bra"), ("i kall februari", "en kall februari"), ("hålla ren miljö", "hålla miljön ren")],
    31: [("antingen... eller", "två val"), ("antingen...eller", "två val"), ("vara ute mer utanför hemmet", "vara utomhus mer"), ("en stor realisation", "en stor rea"), ("fråga efter någon", "fråga någon"), ("en extra tjock strumpa", "ett par extra tjocka strumpor")],
    32: [("skynda på rejält", "skynda mig rejält"), ("flytta ut på stan", "ge mig ut på stan"), ("av en storlek som var enorm", "som var enorma"), ("torka sig själv", "torka sig")],
    33: [("tomsflaska", "tomflaska"), ("hålla hemlig min egen ekonomi", "hålla min egen ekonomi hemlig"), ("i en rad för att vänta på bussen", "i kö för att vänta på bussen")],
    34: [("Urban legends", "Vandringssägner"), ("vid en kant av åkern", "vid kanten av åkern"), ("göra fin middag för en krona", "laga en fin middag för en billig penning"), ("innan vi skulle stänga för kvällen", "innan vi skulle gå och lägga oss")],
    35: [("skådelspelare", "skådespelare"), ("konditional kärlek", "villkorslös kärlek"), ("vem som gjorde denna?", "vem som gjorde den här?")],
    36: [("erbjuda att dekorera hus", "erbjuda mig att dekorera hus"), ("leka skådespelare", "spela död"), ("ännu om tio år", "om tio år")],
    37: [("sin smart mobil", "sin smarta mobil"), (" på engelska kallad en book", "")],
    38: [("i vår telefon", "över telefon"), ("en aktiv fritidsvana", "en aktiv fritid"), ("förvånansvärd stor", "förvånansvärt stor"), ("sätter på mig min skridsko", "sätter på mig mina skridskor"), ("tysta golfspelare", "tysta golfspelarna"), ("jordig mark", "jord")],
    39: [("Kanske de vill", "Kanske vill de"), ("år 1 e.kr. Efter Kristus", "år 1 e.Kr."), ("beställa tid för vila", "ta mig tid för vila")],
    40: [("kuturintresserad", "kulturintresserad")],
    41: [("dektektiv", "detektiv"), ("fri sex", "fritt sex")],
    43: [("välfärdststat", "välfärdsstat")],
    44: [("modern freedom", "modern frihet"), ("rested", "utvilad"), ("omedelbar följd", "omedelbar verkan")],
    45: [("open-minded", "öppensinnad"), ("Mer än en hälft", "Mer än hälften")],
    46: [("norske företagare", "rik norsk företagare"), ("osjyst", "oschyst")],
    47: [("about ekonomi", "om ekonomi")],
    48: [("kommuism", "kommunism"), ("lutheransk", "luthersk")],
    50: [("Vet du om?", "Vet du vad?"), ("vänja min bror vid situationen", "vänja mig vid situationen"), ("en regelbunden tid", "regelbundna tider")],
    51: [("ett enormt stort arrangemang", "ett enormt arrangemang")],
    52: [("mitt uppe i en tyst tanke", "i egna tankar")],
    53: [("väldigt otroligt som precis hände", "något otroligt som precis hände"), ("i en bred skala", "i stor skala")],
    54: [("toppen/underbart/härligt", "toppen"), ("tänk dig/er", "tänk dig")],
    56: [("flintis /flintskallig gubbe", "flintskallig man"), ("flintis/flintskallig gubbe", "flintskallig man"), ("hålla kopplad sin aggressiva hund", "hålla sin aggressiva hund kopplad")]
}

def apply():
    with open("sfid_phase2_articles.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    total_replacements = 0
    total_recalcs = 0
    
    for step in data.get("steps", []):
        for article in step.get("articles", []):
            art_id_str = article["article_id"].replace("art_", "")
            try:
                art_id = int(art_id_str)
            except ValueError:
                continue
                
            if art_id in replacements:
                reps = replacements[art_id]
                for old_text, new_text in reps:
                    # Check sentences
                    for sentence in article.get("sentences", []):
                        if old_text in sentence["sv"]:
                            sentence["sv"] = sentence["sv"].replace(old_text, new_text)
                            total_replacements += 1
                            
                            # Need to update word_in_sentence if it was modified
                            for target in sentence.get("target_words", []):
                                if target["word_in_sentence"] == old_text:
                                    target["word_in_sentence"] = new_text
                                elif old_text in target["word_in_sentence"]:
                                    target["word_in_sentence"] = target["word_in_sentence"].replace(old_text, new_text)
                                    
    # Now recalculate positions for ALL articles to ensure absolute correctness
    for step in data.get("steps", []):
        for article in step.get("articles", []):
            for sentence in article.get("sentences", []):
                sv_text = sentence["sv"]
                for target in sentence.get("target_words", []):
                    word = target["word_in_sentence"]
                    idx = sv_text.find(word)
                    if idx != -1:
                        target["position_start"] = idx
                        target["position_end"] = idx + len(word)
                        total_recalcs += 1
                    else:
                        print(f"WARNING: Cannot find '{word}' in sentence: {sv_text}")
    
    with open("sfid_phase2_articles_v2.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Done. Made {total_replacements} replacements. Recalculated {total_recalcs} target words.")

if __name__ == "__main__":
    apply()
