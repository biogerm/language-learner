import json
import re

text = """Vi befann oss i en vacker och nästan orörd del av Norden. Det var en suggestiv miljö. Vi började dagen vid en vacker näckrosdamm i en grön dal. Det var himla vackert, och vi kunde andas frisk luft. På ett litet grässtrå kröp en myra. På bergets sydsida lyste solen. "Oj då," sa vår guide, "titta där!" 

En stor björn, närmare bestämt en brunbjörn, rörde sig i skogen. Bredvid låg ett kadaver som den skulle äta. "Det är i princip omöjligt att se dem så här," sa vår zoolog. Han tyckte om både…och när det gällde växter och djur. Vi såg också en ren och ett litet får. En ståtlig älg och en liten älgkalv stod i skogsbrynet. En varg, eller ulv som man förr sa, ylade i fjärran. Skogen var så tät att man var tvungen att be om hjälp för att hitta ut. Jag fick lust att gå närmare kanten, men jag stannade strax innan en brant klippa. Där fanns is på marken. 

Vår botaniker visade oss en sällsynt växt, en vacker kaprifol. Han berättade hur man kunde skydda den. "Vi måste öva på att ta hand om naturen utan att förstöra den." Han ritade ett mönster på ett papper. Han förklarade skillnaden mellan en hanne och en hona hos vissa blommor. I vattnet nedanför simmade en ål, men som tur var ingen krokodil! I havet långt borta kunde vi se en delfin.

Vi hade med oss en hund, en glad pudel, och såg en färgglad påfågel vid en gård. Vi upptäckte också en spindel, en fästing och en surrande geting. Plötsligt såg vi en orm och en stor oxe på fältet. "Ett stort antal av de djur vi sett är däggdjur," sa guiden.

Man ville behålla rätt temperatur i stugan, men ute började det sjunka redan på eftermiddagen. Vi fick se en stor andel av detta område på tjugo kvadratkilometer. En spanske turist var med oss. Han var nykterist och drack bara vatten, en fantastisk lokal råvara. När dagen var slut bad han oss att ge respons på hans svenska. Detta var min femte resa hit, och jag kommer åka hit igen!"""

core_words = [
    "växt", "hanne", "ren", "ål", "spindel", "älgkalv", "myra", "får", "orm", "oxe", 
    "älg", "geting", "kadaver", "hona", "björn", "fästing", "brunbjörn", "ulv", 
    "krokodil", "zoolog", "klippa", "brant", "kaprifol", "delfin", "botaniker", 
    "tät", "grässtrå", "is", "kvadratkilometer", "dal", "luft", "sydsida", 
    "påfågel", "pudel", "orörd", "däggdjur", "råvara", "temperatur", "näckrosdamm"
]

glue_words = [
    "spanske", "strax innan", "Norden", "himla", "öva på", "antal", "ge respons", 
    "redan", "be om hjälp", "utan att", "både…och", "i princip", "skydda", "andel", 
    "papper", "suggestiv", "få lust", "femte", "igen", "nykterist", "oj då"
]

target_mappings = [
    # Core
    ("växt", "växt"),
    ("hanne", "hanne"),
    ("ren", "ren"),
    ("ål", "ål"),
    ("spindel", "spindel"),
    ("älgkalv", "älgkalv"),
    ("myra", "myra"),
    ("får", "får"),
    ("orm", "orm"),
    ("oxe", "oxe"),
    ("älg", "älg"),
    ("geting", "geting"),
    ("kadaver", "kadaver"),
    ("hona", "hona"),
    ("björn", "björn"),
    ("fästing", "fästing"),
    ("brunbjörn", "brunbjörn"),
    ("ulv", "ulv"),
    ("krokodil", "krokodil"),
    ("zoolog", "zoolog"),
    ("klippa", "klippa"),
    ("brant", "brant"),
    ("kaprifol", "kaprifol"),
    ("delfin", "delfin"),
    ("botaniker", "botaniker"),
    ("tät", "tät"),
    ("grässtrå", "grässtrå"),
    ("is", "is"),
    ("kvadratkilometer", "kvadratkilometer"),
    ("dal", "dal"),
    ("luft", "luft"),
    ("sydsida", "sydsida"),
    ("påfågel", "påfågel"),
    ("pudel", "pudel"),
    ("orörd", "orörd"),
    ("däggdjur", "däggdjur"),
    ("råvara", "råvara"),
    ("temperatur", "temperatur"),
    ("näckrosdamm", "näckrosdamm"),

    # Glue
    ("spanske", "spanske"),
    ("strax innan", "strax innan"),
    ("Norden", "Norden"),
    ("himla", "himla"),
    ("öva på", "öva på"),
    ("antal", "antal"),
    ("ge respons", "ge respons"),
    ("redan", "redan"),
    ("be om hjälp", "be om hjälp"),
    ("utan att", "utan att"),
    ("både…och", "både…och"),
    ("i princip", "i princip"),
    ("skydda", "skydda"),
    ("andel", "andel"),
    ("papper", "papper"),
    ("suggestiv", "suggestiv"),
    ("få lust", "fick lust"),
    ("femte", "femte"),
    ("igen", "igen"),
    ("nykterist", "nykterist"),
    ("oj då", "Oj då")
]

words_json = []

for base, word_in_sentence in target_mappings:
    if base == "ren":
        start = text.find("också en ren") + 9
    elif base == "får":
        start = text.find("litet får") + 6
    elif base == "älg":
        start = text.find("ståtlig älg") + 8
    elif base == "orm":
        start = text.find("en orm") + 3
    elif base == "oxe":
        start = text.find("stor oxe") + 5
    elif base == "is":
        start = text.find("fanns is") + 6
    elif base == "luft":
        start = text.find("frisk luft") + 6
    elif base == "både…och":
        start = text.find("både…och")
    elif " " in word_in_sentence or "." in word_in_sentence or "?" in word_in_sentence or "!" in word_in_sentence or "…" in word_in_sentence or "”" in word_in_sentence or "-" in word_in_sentence or "–" in word_in_sentence:
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
    "step_id": "natur_miljö",
    "step_title": "Natur & Miljö",
    "article_id": "art_21",
    "sv": text,
    "target_words": words_json,
    "primary_words_used": core_words + glue_words
}

with open('./course/sfid/phase2/article_21.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("SUCCESS")
