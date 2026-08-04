import json

with open("final_semantic_dictionary.json", "r", encoding="utf-8") as f:
    master_dict = json.load(f)
    master_words = set()
    for k, v in master_dict.items():
        master_words.update(v)
        
with open("sfid_phase2_articles.json", "r", encoding="utf-8") as f:
    course = json.load(f)
    
used_words = set()
for step in course["steps"]:
    for article in step["articles"]:
        used_words.update(article["primary_words_used"])
        
missing = master_words - used_words
print(f"Total Master Words: {len(master_words)}")
print(f"Total Used Words: {len(used_words)}")
print(f"Missing Words: {len(missing)}")

with open("global_glue_pool.json", "r", encoding="utf-8") as f:
    glue_pool = json.load(f)
    print(f"In Glue Pool: {len(glue_pool)}")
    
missing_not_in_glue = missing - set(glue_pool)
print(f"Missing NOT in Glue Pool: {len(missing_not_in_glue)}")
if missing_not_in_glue:
    print(list(missing_not_in_glue))
