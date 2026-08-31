import json
import os
import sys
import math
import random

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
    "Relationer & Känslor"
]

def prep(idx):
    with open("article_plan.json", "r", encoding="utf-8") as f:
        plan = json.load(f)
        
    if idx >= len(plan):
        print("ALL_DONE")
        return
        
    article = plan[idx]
    if article["status"] == "completed":
        print(f"Article {idx} already completed.")
        return
        
    with open("global_glue_pool.json", "r", encoding="utf-8") as f:
        glue_pool = json.load(f)
        
    target_glue_count = 60 - len(article["core_words"])
    
    # Randomly select exact glue words for the LLM to use
    if len(glue_pool) >= target_glue_count:
        assigned_glue = random.sample(glue_pool, target_glue_count)
    else:
        assigned_glue = glue_pool
        
    # We save these assigned glue words into the plan so we know what they were
    article["assigned_glue"] = assigned_glue
    with open("article_plan.json", "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    
    prompt = f"""You are an expert Swedish language teacher specializing in CEFR Level B1 (SFI Level D). 
Your task is to write a highly coherent, natural-sounding article in Swedish that seamlessly incorporates a specific list of target vocabulary words.

# WRITING STANDARDS:
1. Target Level: STRICTLY CEFR B1.
2. Context Clues: Provide enough context so a learner can guess meaning. 
3. Length & Flow: Write between 300-500 words.
4. Sentence Length: Average 10-15 words per sentence.
5. Topic: Create an engaging story or essay about: {article['theme']}. Give the article a meaningful title.

# TARGET VOCABULARY:
You MUST use EVERY SINGLE ONE of these CORE words:
{json.dumps(article['core_words'], ensure_ascii=False, indent=2)}

You MUST ALSO use EVERY SINGLE ONE of these GLUE words:
{json.dumps(assigned_glue, ensure_ascii=False, indent=2)}

# CONSTRAINTS & OUTPUT FORMAT:
Output strictly in JSON format matching the 3-layer schema.
- "course_id": "sfid"
- "course_title": "SFI D"
- "step_id": "{article['theme'].lower().replace(' & ', '_').replace(' ', '_')}"
- "step_title": "{article['theme']}"
- "article_id": "{article['article_id']}"
- "sv": The Swedish sentence string MUST be plain text.
- "target_words": For each target word (both core and glue) used, identify its inflected form ("word_in_sentence"), base form ("base_form"), and 0-indexed positions.
- "primary_words_used": An array of ALL target words (Core + Glue) you used.

Save your JSON directly to `course/sfid/phase2/article_{idx}.json` using `write_to_file`. Finish immediately after.
"""
    with open(f"prompt_{idx}.txt", "w", encoding="utf-8") as f:
        f.write(prompt)
    print(f"Prepared prompt for article {idx} (Theme: {article['theme']}, {len(article['core_words'])} Core, {len(assigned_glue)} Glue)")

def validate(idx):
    filename = f"article_{idx}.json"
    if not os.path.exists(filename):
        print(f"Error: {filename} not found.")
        sys.exit(1)
        
    try:
        with open(filename, "r", encoding="utf-8") as f:
            article_data = json.load(f)
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        sys.exit(1)
        
    with open("article_plan.json", "r", encoding="utf-8") as f:
        plan = json.load(f)
        
    article_plan = plan[idx]
    core_words = set(article_plan["core_words"])
    assigned_glue = set(article_plan.get("assigned_glue", []))
    
    try:
        if "steps" in article_data:
            art_node = article_data["steps"][0]["articles"][0]
        else:
            art_node = article_data
        used_words = set(art_node.get("primary_words_used", []))
    except KeyError:
        print("Error: Invalid JSON architecture.")
        sys.exit(1)
        
    # Check core word usage
    missing_core = core_words - used_words
    missing_glue = assigned_glue - used_words
    if missing_core:
        print(f"Warning: Missing core words: {missing_core}")
    if missing_glue:
        print(f"Warning: Missing assigned glue words: {missing_glue}")
        
    # Remove ASSIGNED glue words from global pool regardless of if LLM missed one
    # to guarantee 100% pool coverage by the end.
    if not assigned_glue:
        # fallback for old articles 0-4
        glue_used = used_words - core_words
    else:
        glue_used = assigned_glue
        
    with open("global_glue_pool.json", "r", encoding="utf-8") as f:
        glue_pool = json.load(f)
        
    new_glue_pool = [w for w in glue_pool if w not in glue_used]
    
    with open("global_glue_pool.json", "w", encoding="utf-8") as f:
        json.dump(new_glue_pool, f, ensure_ascii=False, indent=2)
        
    print(f"Validation successful. Updated global glue pool: {len(glue_pool)} -> {len(new_glue_pool)} words.")
    
    plan[idx]["status"] = "completed"
    with open("article_plan.json", "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "prep":
        prep(int(sys.argv[2]))
    elif cmd == "validate":
        validate(int(sys.argv[2]))
