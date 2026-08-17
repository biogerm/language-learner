import json, glob, os
base_dir = "course/sfid"
dict_path = os.path.join(base_dir, "phase1", "master_dictionary.json")
with open(dict_path, "r", encoding="utf-8") as f:
    master_data = json.load(f)["words"]

primary_words = set(master_data.keys())
extracted_contexts = {}
articles_pattern = os.path.join(base_dir, "phase2", "articles_translated", "art_*.json")
for file_path in glob.glob(articles_pattern):
    with open(file_path, "r", encoding="utf-8") as f:
        article_data = json.load(f)
        for s in article_data.get("sentences", []):
            for tw in s.get("target_words", []):
                base_form = tw.get("base_form", "")
                if base_form in primary_words:
                    extracted_contexts[base_form] = 1

count = 0
missing = []
for base_form in master_data.keys():
    if base_form in extracted_contexts:
        count += 1
    else:
        missing.append(base_form)

print(f"Words in extracted_contexts: {count}")
print(f"Missing words: {len(missing)}")
