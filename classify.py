import json
import re

with open("./course/sfid/phase2/chunk_2.json") as f:
    data = json.load(f)

themes = {
    "Vardagsliv": [],
    "Arbetsliv": [],
    "Hälsa & Medicin": [],
    "Natur & Miljö": [],
    "Samhälle & Politik": [],
    "Kultur & Nöje": [],
    "Relationer & Känslor": [],
    "Vetenskap & Teknik": [],
    "Resor & Transport": [],
    "Mat & Matlagning": [],
    "Utbildning": [],
    "Abstrakta Koncept": []
}

def classify(sv, en):
    sv_lower = sv.lower()
    en_lower = en.lower()
    
    # Food & Cooking
    if re.search(r'\b(food|cook|eat|drink|restaurant|fruit|vegetable|meat|candy|sugar|sweet|taste|chew|chocolate|praline|coffee|tea|beer|wine|water|cake|pie|apple|meal|breakfast|lunch|dinner|hungry|thirsty|boil|fry|bake)\b', en_lower) or re.search(r'(mat|dryck|godis|socker|frukt|grönsak|kött|äta|dricka|hungrig|törstig|smak|tårta|choklad|kaka)', sv_lower):
        return "Mat & Matlagning"
        
    # Health & Medicine
    if re.search(r'\b(health|medicine|sick|doctor|hospital|pain|body|disease|illness|tooth|dental|caries|blood|brain|heart|muscle|pill|drug|addiction|smoke|cigarette|care|nurse)\b', en_lower) or re.search(r'(hälsa|medicin|sjuk|läkare|sjukhus|smärta|kropp|tand|karies|blod|hjärta|muskel|piller|drog|beroende|rök|cigarett|vård)', sv_lower):
        return "Hälsa & Medicin"
        
    # Society & Politics
    if re.search(r'\b(society|politics|government|minister|party|law|vote|election|democra|republic|king|queen|prince|royal|power|state|citizen|tax|economy|public|parliament|dictator|leader|welfare|pension|subsidy)\b', en_lower) or re.search(r'(samhälle|politik|regering|minister|parti|lag|röst|val|demokrati|republik|kung|drottning|prins|makt|stat|medborgare|skatt|ekonomi|offentlig|parlament|diktator|ledare|välfärd|pension|bidrag)', sv_lower):
        return "Samhälle & Politik"
        
    # Work life
    if re.search(r'\b(work|job|money|office|boss|company|salary|employ|business|career|colleague|industry|factory|manager|worker|profession)\b', en_lower) or re.search(r'(arbete|jobb|pengar|kontor|chef|företag|lön|anställa|affär|karriär|kollega|industri|fabrik|arbetare|yrke)', sv_lower):
        return "Arbetsliv"
        
    # Nature & Environment
    if re.search(r'\b(nature|environment|tree|animal|climate|pollution|sea|ocean|forest|mountain|river|lake|flower|bird|fish|dog|cat|weather|sun|rain|snow|wind|earth|planet|moon|space|star|ecology)\b', en_lower) or re.search(r'(natur|miljö|träd|djur|klimat|förorening|hav|skog|berg|flod|sjö|blomma|fågel|fisk|hund|katt|väder|sol|regn|snö|vind|jord|planet|måne|rymd|stjärna|ekologi)', sv_lower):
        return "Natur & Miljö"
        
    # Culture & Entertainment
    if re.search(r'\b(culture|entertainment|music|film|art|museum|read|play|game|movie|cinema|theatre|concert|book|song|dance|festival|party|fun|leisure|sport)\b', en_lower) or re.search(r'(kultur|nöje|musik|film|konst|museum|läsa|spela|spel|bio|teater|konsert|bok|sång|dansa|festival|fest|rolig|fritid|sport)', sv_lower):
        return "Kultur & Nöje"
        
    # Relationships & Emotions
    if re.search(r'\b(relationship|emotion|friend|family|love|hate|angry|sad|happy|feel|marriage|wife|husband|mother|father|child|sister|brother|glad|cry|laugh|kiss|hug|together|lonely)\b', en_lower) or re.search(r'(relation|känsla|vän|familj|kärlek|hata|arg|ledsen|glad|känna|äktenskap|fru|man|mor|far|barn|syster|bror|gråta|skratta|kyss|kram|tillsammans|ensam)', sv_lower):
        return "Relationer & Känslor"
        
    # Education
    if re.search(r'\b(education|school|university|student|teacher|study|learn|class|lesson|exam|degree|academic|science|research)\b', en_lower) or re.search(r'(utbildning|skola|universitet|student|elev|lärare|studera|lära|klass|lektion|examen|akademisk|vetenskap|forskning)', sv_lower):
        return "Utbildning"
        
    # Science & Technology
    if re.search(r'\b(technology|computer|internet|physics|chemistry|biology|engineering|machine|software|hardware|digital|device|screen|phone)\b', en_lower) or re.search(r'(teknik|dator|internet|fysik|kemi|biologi|ingenjör|maskin|mjukvara|hårdvara|digital|apparat|skärm|telefon)', sv_lower):
        return "Vetenskap & Teknik"
        
    # Travel & Transport
    if re.search(r'\b(travel|transport|car|bus|train|flight|hotel|tourist|ticket|station|airport|road|street|drive|ride|fly|walk|journey|trip)\b', en_lower) or re.search(r'(resa|transport|bil|buss|tåg|flyg|hotell|turist|biljett|station|flygplats|väg|gata|köra|åka|flyga|gå|promenad)', sv_lower):
        return "Resor & Transport"
        
    # Everyday life
    if re.search(r'\b(everyday|clothes|house|home|furniture|sleep|wake|routine|buy|store|shop|clean|wash|wear|shirt|pants|shoes|bed|chair|table|room|door|window)\b', en_lower) or re.search(r'(vardag|kläder|hus|hem|möbel|sova|vakna|rutin|köpa|butik|affär|handla|städa|tvätta|bära|skjorta|byxor|skor|säng|stol|bord|rum|dörr|fönster)', sv_lower):
        return "Vardagsliv"
        
    # Abstract Concepts (Fallback for generic words, phrases, prepositions, numbers, etc)
    return "Abstrakta Koncept"

for item in data:
    sv = item.get("sv", "")
    en = item.get("en", "")
    category = classify(sv, en)
    themes[category].append(sv)

# Verify all words are included
total_clustered = sum(len(v) for v in themes.values())
if total_clustered != len(data):
    print(f"Error: {total_clustered} words clustered out of {len(data)}")

with open("temp.json", "w") as f:
    json.dump(themes, f)
print("Saved to temp.json")
