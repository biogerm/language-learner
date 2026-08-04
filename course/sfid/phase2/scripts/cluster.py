import json
import sys

def get_theme(sv, en):
    en_lower = en.lower()
    words = set(en_lower.replace(',', '').replace('.', '').replace('?', '').replace('!', '').replace('(', '').replace(')', '').replace('/', ' ').split())
    
    # Food & Cooking
    food_kw = {"food", "cook", "cooking", "chocolate", "banana", "carbohydrate", "cookie", "cake", "yoghurt", "eat", "drink", "beer", "soda", "vegetable", "jam", "juice", "salami", "bake", "meal", "breakfast", "lunch", "dinner", "snack", "fruit", "meat", "fish", "bread", "cheese", "milk", "water", "wine", "coffee", "tea", "sugar", "salt", "pepper", "kitchen", "restaurant", "cafe", "menu", "dish", "plate", "fork", "knife", "spoon"}
    if any(kw in en_lower for kw in ["carbohydrate", "yoghurt", "chocolate", "salami", "vegetable", "drink"]):
        return "Mat & Matlagning"
    if words.intersection(food_kw):
        return "Mat & Matlagning"
        
    # Health & Medicine
    health_kw = {"health", "healthy", "medic", "sick", "doctor", "hospital", "ill", "pain", "hurt", "muscle", "knee", "leg", "weight", "exercise", "workout", "fitness", "sweat", "tired", "sleep", "heart", "overdose", "suicide", "blood", "body", "diet", "fit", "gym", "stretch", "sore", "disease", "pill", "drug", "care", "patient", "nurse", "athletic", "relax"}
    if any(kw in en_lower for kw in ["health", "workout", "fitness", "overdose", "suicide", "muscle"]):
        return "Hälsa & Medicin"
    if words.intersection(health_kw):
        return "Hälsa & Medicin"

    # Education
    edu_kw = {"educat", "school", "university", "student", "study", "learn", "teach", "course", "degree", "class", "grammar", "adjective", "noun", "pronoun", "word", "sentence", "language", "math", "teacher", "professor", "lesson", "exam", "test", "grade", "book", "read", "write", "note", "paper", "pen", "pencil", "desk", "board", "homework", "question", "answer", "explain", "dictionary", "translate", "phrase"}
    if any(kw in en_lower for kw in ["educat", "universit", "grammar", "adjective", "noun", "pronoun", "math", "study", "student"]):
        return "Utbildning"
    if words.intersection(edu_kw):
        return "Utbildning"

    # Resor & Transport
    travel_kw = {"travel", "transport", "bus", "train", "flight", "fly", "car", "drive", "ride", "trip", "vacation", "luggage", "hotel", "beach", "city", "street", "map", "compass", "railway", "road", "path", "way", "tour", "visit", "guide", "ticket", "station", "airport", "port", "ship", "boat", "bike", "bicycle", "walk", "run", "hike", "abroad", "foreign"}
    if any(kw in en_lower for kw in ["vacation", "luggage", "compass", "railway", "tourist"]):
        return "Resor & Transport"
    if words.intersection(travel_kw):
        return "Resor & Transport"

    # Arbetsliv
    work_kw = {"work", "job", "career", "boss", "colleague", "employ", "profession", "industry", "finance", "earn", "salary", "pay", "tax", "unemployment", "office", "company", "business", "meeting", "director", "manager", "worker", "labor", "internship", "colleagues", "union", "colleague"}
    if any(kw in en_lower for kw in ["career", "industry", "unemployment", "colleague", "internship", "salary", "work"]):
        return "Arbetsliv"
    if words.intersection(work_kw):
        return "Arbetsliv"

    # Kultur & Nöje
    culture_kw = {"cultur", "cultural", "entertain", "art", "music", "sport", "game", "book", "film", "movie", "theater", "dance", "sing", "paint", "draw", "museum", "gallery", "exhibition", "novel", "poetry", "photo", "magic", "party", "ball", "play", "actor", "actress", "stage", "performance", "concert", "festival", "club", "bar", "restaurant", "choir", "chess", "orchestra", "painting", "artist", "drawing", "exhibit"}
    if any(kw in en_lower for kw in ["cultur", "museum", "exhibition", "poetry", "gallery", "theater", "paint", "dance", "sing", "art "]):
        return "Kultur & Nöje"
    if words.intersection(culture_kw):
        return "Kultur & Nöje"

    # Natur & Miljö
    nature_kw = {"nature", "environ", "animal", "plant", "tree", "flower", "rose", "mountain", "sea", "ocean", "weather", "snow", "rain", "sun", "space", "dog", "butterfly", "garden", "outdoor", "bird", "fish", "forest", "river", "lake", "climate", "earth", "world", "sky", "star", "moon", "pet", "farm", "agriculture", "mining", "forestry"}
    if any(kw in en_lower for kw in ["nature", "mountain", "butterfly", "agriculture", "forestry"]):
        return "Natur & Miljö"
    if words.intersection(nature_kw):
        return "Natur & Miljö"

    # Samhälle & Politik
    society_kw = {"societ", "politic", "parliament", "law", "police", "state", "nation", "class", "bourgeois", "king", "queen", "history", "legal", "economic", "organization", "club", "government", "vote", "election", "citizen", "public", "community", "social", "power", "rule", "leader", "president", "minister", "court", "judge", "crime", "murder", "scandal", "jewish", "religion", "religious", "church"}
    if any(kw in en_lower for kw in ["parliament", "bourgeois", "scandal", "politic", "societ", "murder", "economic", "history", "legal"]):
        return "Samhälle & Politik"
    if words.intersection(society_kw):
        return "Samhälle & Politik"

    # Relationer & Känslor
    relation_kw = {"relation", "emotion", "friend", "family", "love", "hate", "feel", "happy", "sad", "angry", "marry", "divorce", "wife", "husband", "brother", "sister", "parent", "child", "alone", "socialize", "meet", "talk", "chat", "kiss", "hug", "smile", "cry", "laugh", "fear", "scare", "hope", "wish", "want", "need", "like", "dislike", "care", "miss", "sorry", "forgive", "thank", "please", "glad", "relationship", "married", "boyfriend", "girlfriend", "wedding", "enemy", "agree"}
    if any(kw in en_lower for kw in ["friend", "family", "marry", "divorce", "forgive", "socialize", "love", "hate", "feel", "happy"]):
        return "Relationer & Känslor"
    if words.intersection(relation_kw):
        return "Relationer & Känslor"

    # Vetenskap & Teknik
    tech_kw = {"scienc", "technolog", "computer", "internet", "phone", "email", "sms", "machine", "invent", "research", "experiment", "data", "software", "hardware", "network", "web", "app", "digital", "screen", "tv", "television", "radio", "electric", "power", "energy"}
    if any(kw in en_lower for kw in ["technolog", "computer", "internet", "email", "sms", "television", "tv "]):
        return "Vetenskap & Teknik"
    if words.intersection(tech_kw):
        return "Vetenskap & Teknik"

    # Vardagsliv
    everyday_kw = {"everyday", "life", "home", "house", "clean", "wash", "shower", "dress", "clothes", "shoe", "hair", "shave", "comb", "buy", "sell", "money", "time", "day", "night", "morning", "evening", "habit", "hobby", "wake", "bed", "living", "routine", "clock", "hour", "minute", "week", "month", "year", "today", "tomorrow", "yesterday", "always", "never", "often", "sometimes", "usually", "clean", "dirty", "apartment", "household", "housework"}
    if any(kw in en_lower for kw in ["everyday", "household", "housework", "apartment", "clothes", "time", "day ", "night"]):
        return "Vardagsliv"
    if words.intersection(everyday_kw):
        return "Vardagsliv"
        
    return "Abstrakta Koncept"

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

with open('./course/sfid/phase2/chunk_1.json', 'r') as f:
    data = json.load(f)

for item in data:
    sv = item["sv"]
    en = item["en"]
    theme = get_theme(sv, en)
    themes[theme].append(sv)

# We print the json string out, nicely formatted to 4 spaces, so the LLM can copy it.
out = json.dumps(themes, indent=4, ensure_ascii=False)
with open('temp_cluster.json', 'w') as f:
    f.write(out)
