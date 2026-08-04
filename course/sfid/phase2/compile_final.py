import json
import os

THEME_ORDER = [
    "Vetenskap & Teknik",
    "Resor & Transport",
    "Arbetsliv",
    "Utbildning",
    "Mat & Matlagning",
    "Natur & Miljö",
    "Hälsa & Medicin",
    "Vardagsliv",
    "Kultur & Nöje",
    "Samhälle & Politik",
    "Relationer & Känslor",
    "Blandade Ämnen (Mixed Topics)"
]

def format_step_id(theme):
    return theme.lower().replace(' & ', '_').replace(' ', '_')

def compile_articles():
    course = {
        "course_id": "sfid",
        "course_title": "SFI D",
        "steps": []
    }
    
    # Pre-populate steps in the correct order
    step_map = {}
    for i, theme in enumerate(THEME_ORDER):
        step_id = format_step_id(theme)
        step_obj = {
            "step_id": f"step_{(i+1):02d}",
            "step_title": theme,
            "articles": []
        }
        course["steps"].append(step_obj)
        step_map[step_id] = step_obj

    total_words_used = set()
    total_articles = 0
    
    distribution = {theme: 0 for theme in THEME_ORDER}

    for i in range(57):
        filename = f"article_{i}.json"
        if not os.path.exists(filename):
            print(f"Missing {filename}")
            continue
            
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        # Standardize step_id from the file
        step_title = data.get("step_title", "")
        # fallback step_id if missing or mismatch
        step_id = format_step_id(step_title)
        
        if step_id not in step_map:
            print(f"Warning: Unknown step {step_title} in {filename}")
            # put in a default
            step_id = format_step_id(THEME_ORDER[-1])
            
        primary_words = data.get("primary_words_used", [])
        
        # Build the article object
        article_obj = {
            "article_id": data.get("article_id", f"art_{i:02d}"),
            "article_title": "Läsförståelse",
            "target_word_count": len(primary_words),
            "sentences": [
                {
                    "sentence_id": f"art{i:02d}_s001",
                    "sv": data.get("sv", ""),
                    "en": "",
                    "target_words": data.get("target_words", [])
                }
            ],
            "primary_words_used": primary_words,
            "secondary_words_used": []
        }
        
        step_map[step_id]["articles"].append(article_obj)
        total_words_used.update(primary_words)
        total_articles += 1
        if step_title in distribution:
            distribution[step_title] += len(primary_words)

    # Validate against dictionary
    master_words = set()
    try:
        with open("final_semantic_dictionary.json", "r", encoding="utf-8") as f:
            master_dict = json.load(f)
            for k, v in master_dict.items():
                master_words.update(v)
    except FileNotFoundError:
        print("final_semantic_dictionary.json not found. Using clustered_dictionary.json to get word counts.")
        with open("clustered_dictionary.json", "r", encoding="utf-8") as f:
            clustered = json.load(f)
        for k, v in clustered.items():
            master_words.update(v)

    missing_words = master_words - total_words_used
    
    # Also add global glue words to master_words since they were randomly drawn from the abstract pool
    with open("global_glue_pool.json", "r", encoding="utf-8") as f:
        remaining_glue = set(json.load(f))
        
    # The true master word set is all categorized words + all abstract words (which were converted to glue pool + specific themes)
    # The orchestrator ensured all specific words + exact glue words were sent. So we should just check the union of total_words_used and remaining_glue vs the total initial dict.
    
    print("=== Validation Results ===")
    print(f"Total Master Words (Categorized): {len(master_words)}")
    print(f"Total Unique Target Words Used: {len(total_words_used)}")
    print(f"Total Articles Generated: {total_articles}")
    if missing_words:
        print(f"Missing categorized words not used (might be in glue pool): {len(missing_words)}")
        
    print("\n=== Word Distribution By Theme ===")
    for theme in THEME_ORDER:
        print(f"{theme}: {distribution[theme]} target words")
        
    print(f"\nRemaining in Global Glue Pool: {len(remaining_glue)} words")

    with open("sfid_phase2_articles.json", "w", encoding="utf-8") as f:
        json.dump(course, f, ensure_ascii=False, indent=2)
    print("\nSaved consolidated JSON to sfid_phase2_articles.json")

if __name__ == "__main__":
    compile_articles()
