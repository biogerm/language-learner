import json
import math
import random

def main():
    # 1. Load the clustered dictionary
    with open("clustered_dictionary.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # 1.5 Load master dictionary to get English meanings
    with open("../phase1/master_dictionary.json", "r", encoding="utf-8") as f:
        master_data = json.load(f)
        sv_to_en = {sv: meta.get("en", "") for sv, meta in master_data["words"].items()}
        
    abstract_words_sv = data.get("Abstrakta Koncept", [])
    abstract_words = [{"sv": w, "en": sv_to_en.get(w, "")} for w in abstract_words_sv]
    
    specific_themes = {k: [{"sv": w, "en": sv_to_en.get(w, "")} for w in v] for k, v in data.items() if k != "Abstrakta Koncept"}
    
    # 2. Define semantic keywords for the 11 themes to catch leaning abstract words
    theme_keywords = {
        "Arbetsliv": ["work", "job", "employ", "boss", "office", "career", "salary", "wage", "profession", "duty", "task", "economic", "finance", "efficient", "organize", "company", "business", "manage", "colleague", "industry", "meeting"],
        "Hälsa & Medicin": ["health", "sick", "ill", "pain", "doctor", "nurse", "hospital", "medicine", "pill", "cure", "heal", "symptom", "disease", "body", "mental", "depress", "stress", "injury", "blood", "patient", "treatment", "care"],
        "Natur & Miljö": ["nature", "environment", "climate", "weather", "green", "pollution", "tree", "animal", "plant", "earth", "water", "sea", "forest", "global", "warm", "recycle", "energy", "sun", "rain"],
        "Samhälle & Politik": ["society", "politic", "law", "govern", "vote", "elect", "citizen", "right", "public", "state", "country", "nation", "crime", "police", "court", "justice", "economy", "tax", "policy", "social", "democrat"],
        "Kultur & Nöje": ["culture", "art", "music", "film", "movie", "book", "read", "paint", "draw", "dance", "theatre", "entertainment", "fun", "game", "play", "sport", "hobby", "festival", "concert"],
        "Relationer & Känslor": ["relation", "friend", "family", "love", "hate", "feel", "emotion", "marry", "divorce", "partner", "couple", "happy", "sad", "angry", "fear", "trust", "care", "hug", "kiss", "argue"],
        "Vetenskap & Teknik": ["science", "tech", "computer", "internet", "software", "hardware", "machine", "device", "research", "experiment", "discover", "invent", "data", "digital", "network", "system", "lab"],
        "Resor & Transport": ["travel", "trip", "journey", "transport", "car", "bus", "train", "flight", "fly", "airport", "station", "road", "street", "drive", "ride", "ticket", "hotel", "tourist", "visit", "luggage"],
        "Mat & Matlagning": ["food", "cook", "eat", "drink", "meal", "breakfast", "lunch", "dinner", "restaurant", "recipe", "ingredient", "meat", "veg", "fruit", "bake", "kitchen", "taste", "delicious", "hungry", "thirsty"],
        "Utbildning": ["education", "school", "teach", "learn", "student", "teacher", "class", "course", "study", "exam", "test", "grade", "university", "college", "degree", "knowledge", "science"],
        "Vardagsliv": ["daily", "life", "home", "house", "clean", "wash", "sleep", "wake", "morning", "evening", "clothes", "wear", "shop", "buy", "sell", "routine", "habit", "apartment", "furniture"]
    }
    
    # Target ratios
    total_concrete = sum(len(v) for v in specific_themes.values())
    total_abstract = len(abstract_words)
    ratio = total_abstract / total_concrete
    
    # Calculate target capacities for each theme
    targets = {}
    for theme, words in specific_themes.items():
        targets[theme] = {
            "concrete_count": len(words),
            "target_abstract": round(len(words) * ratio),
            "allocated_semantic": [],
            "allocated_glue": []
        }
    
    # 3. Semantic Pass: Distribute leaning words
    pure_glue = []
    
    for word_obj in abstract_words:
        en_meaning = word_obj.get("en", "").lower()
        
        assigned = False
        # Tokenize english meaning broadly
        
        for theme, keywords in theme_keywords.items():
            if any(kw in en_meaning for kw in keywords):
                # Check if we haven't exceeded target by too much (allow a bit of overflow for semantics)
                if len(targets[theme]["allocated_semantic"]) < targets[theme]["target_abstract"]:
                    targets[theme]["allocated_semantic"].append(word_obj)
                    assigned = True
                    break
        
        if not assigned:
            pure_glue.append(word_obj)
            
    # 4. Balancing Pass: Distribute pure glue to meet targets
    random.seed(42)
    random.shuffle(pure_glue)
    
    for theme in targets:
        needed = targets[theme]["target_abstract"] - len(targets[theme]["allocated_semantic"])
        if needed > 0:
            # take 'needed' amount from pure_glue
            chunk = pure_glue[:needed]
            pure_glue = pure_glue[needed:]
            targets[theme]["allocated_glue"].extend(chunk)
            
    # If any pure glue left over (due to rounding), distribute evenly
    idx = 0
    theme_keys = list(targets.keys())
    while pure_glue:
        targets[theme_keys[idx % len(theme_keys)]]["allocated_glue"].append(pure_glue.pop(0))
        idx += 1
        
    # 5. Build final dictionary and stats
    final_dict = {}
    stats = []
    
    for theme in targets:
        concrete = specific_themes[theme]
        sem_abs = targets[theme]["allocated_semantic"]
        glue_abs = targets[theme]["allocated_glue"]
        
        total_abs = len(sem_abs) + len(glue_abs)
        final_dict[theme] = concrete + sem_abs + glue_abs
        
        stats.append({
            "theme": theme,
            "concrete": len(concrete),
            "semantic_abs": len(sem_abs),
            "glue_abs": len(glue_abs),
            "total_abs": total_abs,
            "total_words": len(final_dict[theme]),
            "ratio": total_abs / len(concrete) if len(concrete) > 0 else 0
        })
        
    # Write final balanced semantic dictionary
    with open("final_semantic_dictionary.json", "w", encoding="utf-8") as f:
        json.dump(final_dict, f, ensure_ascii=False, indent=2)
        
    # Print stats
    print(f"{'Theme':<25} | {'Concrete':<8} | {'Semantic':<8} | {'Glue':<8} | {'Total Abs':<9} | {'Ratio':<5}")
    print("-" * 75)
    for s in sorted(stats, key=lambda x: x['concrete'], reverse=True):
        print(f"{s['theme'][:24]:<25} | {s['concrete']:<8} | {s['semantic_abs']:<8} | {s['glue_abs']:<8} | {s['total_abs']:<9} | {s['ratio']:.2f}")
    
if __name__ == "__main__":
    main()
