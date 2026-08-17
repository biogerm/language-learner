import json
import os

chunks_dir = "./course/sfid/phase3/data/chunks"

known_ett_words = [
    "sambandsord", "stödord", "tuggmärke", "barndomsminne", "folkhem", "klassamhälle",
    "samförstånd", "barnbidrag", "skattetryck", "samarbete", "styre", "block", "statsråd",
    "departement", "socialbidrag", "län", "självstyre", "funktionshinder", "smultronställe",
    "barnhem", "prov", "ungdomsförbund", "landsting", "lagförslag", "filmmanus", "1900-talet",
    "sommarställe", "smultron", "grässtrå", "vin", "växtnamn", "råd", "fik", "landskapsdjur",
    "skaldjur", "vildmarksområde", "slut", "landskap", "hjortron", "odjur", "nöjesliv", "äventyr",
    "havsbad", "societetshus", "bygge", "havsband", "trähus", "vetemjöl", "fläsk", "smör",
    "tillbehör", "Norrland", "paltbröd", "bröd", "ris", "russin", "salmbär", "björnbär",
    "handelscentrum", "diskotek", "guld", "stry", "kretslopp", "taggmoln", "kroppsarbete",
    "hästkött", "1700-talet", "årtionde", "decennium", "efternamn", "krås", "hjärta",
    "katrinplommon", "perfekt particip", "recept", "avlopp", "fack", "arbetsvillkor",
    "avtal", "preventivmedel", "grannland", "livmedelsföretag", "förbund", "spritförbud",
    "högvarv", "vardagsrum", "nyhetsprogram", "resmål", "arbetsliv", "förbud", "varuhus",
    "slott", "mottagande", "apelsinträd", "verktyg", "århundrade", "sekel", "tempus",
    "tidsschema", "modersmål", "uppbrott", "inuitspråk", "arv", "dokument", "utrikesdepartement",
    "handikapp", "rally", "valspråk", "rike", "stöd", "hopp", "faktum", "massmedium",
    "återbesök", "minne", "kontormaterial", "extrapris", "straff", "skick", "äktenskap",
    "kroppsspråk", "knep", "byggnadsprojekt", "trä", "däggdjur", "skämt", "aprilskämt",
    "syndrom", "proffs", "beteende", "hantverk", "sovrum", "utsläpp", "reningsverk",
    "fordon", "superlativ", "sömnproblem", "köpcentrum", "flygblad", "klimat", "beslut",
    "barnbarn", "parlament", "enfrågeparti", "statsskick", "valmanifest"
]

known_en_words = [
    "partiledare", "förorening", "röst", "tidning", "affisch", "rök", "framtid", "andrahand",
    "andrahandsinformation", "konsekvens", "prognos", "farfar", "jämlikhet", "medborgare",
    "välfärd", "välfärdststat", "tilläggspension", "skala", "ekonomi", "utgift", "kärnkraft",
    "åsikt", "statskupp", "mandatperiod", "månad", "interimsregering", "Moder Svea", "post",
    "riksdagsman", "myndighet", "utrikesminister", "utbildningsminister", "kulturminister",
    "försvarsminister", "miljöminister", "länsstyrelse", "samhällsplanering", "tandvård",
    "kollektivtrafik", "invånare", "barnomsorg", "åldringsvård", "socialtjänst", "svenska för invandrare",
    "statistik", "andel", "två tredjedelar", "hälft", "cykelbana", "tablett", "lärare",
    "klasskompis", "skolpersonal", "skolmat", "grundlag", "regeringsformen", "successionsordningen",
    "tryckfrihetsförordningen", "yttrandefrihetsgrundlagen", "rättighet", "plats", "ministerpost",
    "kommun", "befolkning", "nivå", "rösträtt", "proposition", "ångest", "teatertradition",
    "basker", "regissör", "teaterpjäs", "pjäs", "rad", "höst", "myt", "synd", "scen", "riddare",
    "svärdotter", "paus", "ungdom", "skådespelerska", "släktkrönika", "sol", "grädde", "glass",
    "mjölk", "sylt", "saft", "jordgubbe", "medicin", "trubadur", "botaniker", "geolog", "pedagog",
    "zoolog", "nationalskald", "dikt", "hedersman", "stig", "klippa", "macka", "stämning",
    "rörelse", "sats", "genetivform", "identitet", "turistnäring", "landskapsblomma", "kaprifol",
    "turisinformation", "paviljong", "sträcka", "norska gränsen", "natur", "midnattsol",
    "säl", "själ", "tevebolag", "sjunde plats", "syster", "julfest", "konst", "brist",
    "kommunikation", "tystnad", "parasit", "ö", "norr", "dröm", "favorit", "actionfilm",
    "kärleksfilm", "dokumentär", "snyftare", "komedi", "deckare", "skräckfilm", "favoritfilm",
    "samlingsplats", "brygga", "bryggdans", "bonderepublik", "älv", "världsartist", "musikfestival",
    "same", "sameby", "fysisk aktivitet", "turistort", "mountainbike", "tain", "vintertid",
    "skidåkning", "kunglighet", "kappsegling", "fästning", "fånge", "tjuv", "mördare",
    "järnkula", "fotled", "guidad tur", "suck", "galgbacke", "sommarmånad", "gäst", "luft",
    "sydsida", "hamn", "klimatdebatt", "maträtt", "palt", "potatis", "klick", "grop", "lingonsylt",
    "trötthet", "saffranspannkaka", "pannkaka", "saffran", "ingrediens", "medeltiden", "krydda",
    "lyxvara", "toppklass", "fika", "björkskog", "dal", "vänskapsgåva", "minnesbyggnad", "inbjudan",
    "konst- och industriutställning", "bronsstaty", "utsmyckning", "blomma", "roddbåt",
    "näckrosdamm", "marknad", "thaimat", "föreläsning", "sälsafari", "nationalpark", "äggost",
    "hällristning", "karta", "husmanskost", "matkultur", "vardagsmat", "bondgård", "råvara",
    "köttbulle", "kåldolme", "punkt", "huvudperson", "handling", "framtidstro", "högertrafik",
    "drog", "biograf", "avrättning", "ledamot", "Svenska akademien", "gås", "middag", "festmåltid",
    "timme", "måltid", "vaniljsås", "ingefära", "kryddpeppar", "nejlika", "konjak", "soppa",
    "hals", "mage", "vinge", "gräddsås", "äppelklyfta", "varm choklad", "äggvita", "smet",
    "paprika", "tomat", "persika", "vitlök", "parmesan", "lax", "skinka", "korv", "smörgås",
    "flinga", "havre", "högkonjunktur", "fabrik", "cd-skiva", "vinylskiva", "kärnkraftsolycka",
    "stadsminister", "arbetarfamilj", "elektricitet", "demonstration", "arbetare", "arbetsgivare",
    "berättelse", "Pippi Långstrump", "radiosändning", "varning", "infektionssjukdom", "kust",
    "omröstning", "riksdagsledamot", "kaffe latte", "kön", "diskriminering", "passagerarfärja",
    "oljekris", "kommuism", "miljörörelse", "gröna vågen", "popgrupp", "punkmusik", "Socialstyrelsen",
    "tronföljd", "abort", "miljö- och klimatdebatt", "matlagning", "smart mobil", "hets mot folkgrupp",
    "folkomröstning", "artist", "nyans", "mor", "tron", "systerdotter", "trosinriktning", "lära",
    "festlighet", "vagn", "vetenskapsman", "lunginflammation", "katolik", "abdikation", "påve",
    "kardinal", "ankomst", "sångare", "apelsinträd", "påfågel", "kulle", "sorg", "ungdomskultur",
    "charterresenär", "mellanlandning", "snabbkurs", "serie", "brons", "långbåt", "kristendom",
    "is", "matematik", "astronomi", "pesten", "far", "dotter", "telefon", "kusin", "nordbo",
    "språkfamilj", "kulturella band", "frid och fröjd", "maktkamp", "passfrihet", "språkkonvention",
    "färöiska", "isländska", "germanska", "indoeuropeiska", "urnordiska", "samiska", "finsk-ugriska",
    "ungerska", "estniska", "grönländska", "frihetstiden", "välgörenhet", "personlig tränare",
    "förskola", "golfspelare", "farbror", "grafisk formgivning", "motorsport", "juridik", "vishet",
    "skvallertidning", "faktoid", "skröna", "osanning", "halvsanning", "missuppfattning",
    "guldfisk", "kramp", "tidningsartikel", "toppen", "erfarenhet", "värdering", "reinkarnation",
    "vandringshistoria", "folksaga", "aspekt", "pudel", "mikro", "dam", "lift", "yxa", "minoritet",
    "finlandssvensk", "norrman", "by", "anledning", "datakurs", "folkhögskola", "deklaration",
    "klocka", "prisnivå", "lögn", "snöboll", "lögnare", "hundrakronorssedel", "cirkus", "realisation",
    "plånbok", "lillebror", "belöning", "kyckling", "hjärna", "förvåning", "skepsis", "bur",
    "hårtork", "sportbil", "nolla", "sekreterare", "tendens", "detalj", "näsa", "pupill", "temperatur",
    "grad", "sluss", "kvadratkilometer", "folkmängd", "nöjespark", "berg -och dalbana", "backe",
    "fallvinkel", "skam", "vit lögn", "frisyr", "psykopat", "dagstidning", "färgteve", "strumpa",
    "idrottsstjärna", "mytoman", "kanonkula", "armé", "orsak", "domare", "försöksperson", "forkning",
    "blick", "hyra", "stuga", "fiol", "japan", "engelsman", "resenär", "avkoppling", "flod",
    "utlänning", "hjälte", "kommissarie", "vattenyta", "arkitektur", "sevärdhet", "guldkant",
    "vistelse", "miljard", "följd", "transport", "trädkoja", "hotellägare", "hållbarhet", "kant",
    "dektektiv"
]

misclassified = 0
for c in range(28, 55):
    meta_path = os.path.join(chunks_dir, f"meta_chunk_{c}.json")
    with open(meta_path, "r", encoding="utf-8") as f:
        meta_data = json.load(f)
    
    for word, entry in meta_data.items():
        if entry["word_type"] == "noun":
            g = entry["noun_gender"]
            if word in known_ett_words and g != "ett":
                print(f"[MISMATCH] Chunk {c}: Noun '{word}' expected gender 'ett', found '{g}'")
                entry["noun_gender"] = "ett"
                misclassified += 1
            elif word in known_en_words and g != "en":
                print(f"[MISMATCH] Chunk {c}: Noun '{word}' expected gender 'en', found '{g}'")
                entry["noun_gender"] = "en"
                misclassified += 1
                
    with open(meta_path, "w", encoding="utf-8") as fw:
        json.dump(meta_data, fw, ensure_ascii=False, indent=2)

print(f"Gender verification complete! Fixed {misclassified} gender mismatches.")
