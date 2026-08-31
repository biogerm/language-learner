import json, glob, re, os

print("Step 1: Assembling APP_DATA for sfid...")
sfid_data = {}
articles = sorted(glob.glob("course/sfid/phase2/articles_translated/art_*.json"))

for idx, filepath in enumerate(articles):
    with open(filepath) as f:
        art = json.load(f)
    
    stage = art.get('stage_title') or f"Stage {(idx // 10) + 1}"
    if stage not in sfid_data:
        sfid_data[stage] = {}
        
    topic_title = f"{art.get('article_id', '')}: {art.get('article_title', 'Topic')}"
    
    sentences = []
    for s in art.get("sentences", []):
        sentence_obj = {
            "id": s.get("sentence_id"),
            "sv": s.get("sv"),
            "en": s.get("en"),
            "target_words": s.get("target_words", []),
            "secondary_words": s.get("secondary_words", [])
        }
        sentences.append(sentence_obj)
        
    sfid_data[stage][topic_title] = sentences

# Sort stages by frequency descending
sfid_data = {k: v for k, v in sorted(sfid_data.items(), key=lambda item: len(item[1]), reverse=True)}

legacy_data_path = "../SFI/web_app/data.js"
with open(legacy_data_path, "r") as f:
    legacy_content = f.read()

json_str = re.sub(r"^const\s+APP_DATA\s*=\s*", "", legacy_content).strip()
if json_str.endswith(";"):
    json_str = json_str[:-1]

try:
    app_data = json.loads(json_str)
except json.JSONDecodeError as e:
    print(f"Error parsing legacy data.js: {e}")
    app_data = {}

if "c_sfid" in app_data:
    del app_data["c_sfid"]

app_data["sfid"] = sfid_data

with open(legacy_data_path, "w") as f:
    f.write(f"const APP_DATA = {json.dumps(app_data, indent=4, ensure_ascii=False)};\n")
print(f"Successfully injected 'sfid' into {legacy_data_path}")

print("Step 1.5: Assembling dictation_data.js...")

# Pre-load master dictionary for cross-referencing
master_dict_path = "course/sfid/phase1/master_dictionary.json"
with open(master_dict_path, "r") as f:
    master_dict_raw = json.load(f)

master_dict = {}
for word, info in master_dict_raw.get("words", {}).items():
    master_dict[word] = info.get("en", "")

if not master_dict and isinstance(master_dict_raw, dict):
    master_dict = master_dict_raw

dictation_data_path = "../SFI/web_app/dictation_data.js"
if os.path.exists(dictation_data_path):
    with open(dictation_data_path, "r") as f:
        dict_content = f.read()
    
    dict_json_str = re.sub(r"^const\s+DICTATION_WORDS\s*=\s*", "", dict_content).strip()
    if dict_json_str.endswith(";"):
        dict_json_str = dict_json_str[:-1]
    
    try:
        dict_words_list = json.loads(dict_json_str)
    except json.JSONDecodeError as e:
        print(f"Error parsing legacy dictation_data.js: {e}")
        dict_words_list = []
else:
    dict_words_list = []

# Filter out old sfid/c_sfid data
dict_words_list = [w for w in dict_words_list if w.get("course_id") not in ("c_sfid", "sfid")]

# Add new dictation words
for stage, articles_dict in sfid_data.items():
    for article_title, sentences in articles_dict.items():
        for s in sentences:
            for tw in s.get("target_words", []):
                base_form = tw.get("base_form", "")
                dictionary_en = master_dict.get(base_form, master_dict.get(base_form.lower(), ""))
                dict_words_list.append({
                    "sv": base_form,
                    "en": tw.get("contextual_en", ""),
                    "dictionary_en": dictionary_en,
                    "context_sv": s.get("sv", ""),
                    "stage": stage,
                    "article": article_title,
                    "course_id": "sfid"
                })

with open(dictation_data_path, "w") as f:
    f.write(f"const DICTATION_WORDS = {json.dumps(dict_words_list, indent=4, ensure_ascii=False)};\n")
print(f"Successfully updated dictation_data.js with {len(dict_words_list)} total words.")

print("Step 2: Assembling global_dict.js...")
# master_dict is already pre-loaded above in Step 1.5

global_dict_path = "../SFI/web_app/js/global_dict.js"
with open(global_dict_path, "w") as f:
    f.write(f"const global_dict = {json.dumps(master_dict, indent=4, ensure_ascii=False)};\n")
print(f"Successfully generated {global_dict_path} with {len(master_dict)} entries.")

print("Step 3: Creating audio symlinks in web_app/audio/")
web_app_audio_dir = "../SFI/web_app/audio"
os.makedirs(web_app_audio_dir, exist_ok=True)

# Link sentences_audio
src_sentences = "course/sfid/phase4/output/sentences_audio"
dst_sentences = os.path.join(web_app_audio_dir, "sentences_audio")
if not os.path.exists(dst_sentences):
    os.symlink(src_sentences, dst_sentences)
    print(f"Symlinked {dst_sentences}")

# Link words_audio
src_words = "course/sfid/phase4/output/words_audio"
dst_words = os.path.join(web_app_audio_dir, "words_audio")
if not os.path.exists(dst_words):
    os.symlink(src_words, dst_words)
    print(f"Symlinked {dst_words}")

print("Build complete!")
