import json, glob, os

articles_path = "course/sfid/phase2/articles_translated/art_*.json"
sentences_audio_dir = "course/sfid/phase4/output/sentences_audio"
words_audio_dir = "course/sfid/phase4/output/words_audio"

total_sentences_expected = 0
sentence_ids = set()
target_words_expected = set()

for filepath in glob.glob(articles_path):
    with open(filepath, "r") as f:
        art = json.load(f)
    for s in art.get("sentences", []):
        total_sentences_expected += 1
        sentence_ids.add(s.get("sentence_id"))
        for w in s.get("target_words", []):
            target_words_expected.add(w.get("base_form"))

# Check Sentence Audio Files
sentence_files = glob.glob(f"{sentences_audio_dir}/*.mp3")
sentence_files_valid = 0
sentence_files_invalid = []

for sf in sentence_files:
    sid = os.path.basename(sf).replace(".mp3", "")
    size = os.path.getsize(sf)
    if size > 1024:  # At least 1KB to be considered valid
        sentence_files_valid += 1
    else:
        sentence_files_invalid.append(sf)

missing_sentence_audio = [sid for sid in sentence_ids if not os.path.exists(f"{sentences_audio_dir}/{sid}.mp3")]

# Check Word Audio Files for Target Words
target_words_valid = 0
target_words_invalid = []
missing_target_word_audio = []

for tw in target_words_expected:
    # We need to find if the word audio exists. 
    # The file name is usually some sanitized version. Let's look up the manifest.
    pass

with open("course/sfid/phase4/output/audio_manifest.json", "r") as f:
    manifest = json.load(f)
    
word_manifest = manifest.get("words", {})

for tw in target_words_expected:
    if tw in word_manifest:
        file_path = f"course/sfid/phase4/output/{word_manifest[tw].get('file')}"
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            if size > 1024:
                target_words_valid += 1
            else:
                target_words_invalid.append(tw)
        else:
            missing_target_word_audio.append(tw)
    else:
        missing_target_word_audio.append(tw)

print(f"Total Sentences in Articles: {total_sentences_expected}")
print(f"Total Sentence Audio Files Generated (Total on Disk): {len(sentence_files)}")
print(f"Valid Sentence Audio Files (>1KB): {sentence_files_valid}")
print(f"Invalid Sentence Audio Files: {len(sentence_files_invalid)}")
print(f"Missing Sentence Audio Files (Not Generated): {len(missing_sentence_audio)}")

print("-" * 30)
print(f"Total Unique Target Words in Articles: {len(target_words_expected)}")
print(f"Valid Word Audio Files for Target Words (>1KB): {target_words_valid}")
print(f"Invalid Word Audio Files for Target Words: {len(target_words_invalid)}")
print(f"Missing Word Audio Files for Target Words (Not Generated): {len(missing_target_word_audio)}")
