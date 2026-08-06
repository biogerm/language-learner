import json, glob, os

articles_path = "course/sfid/phase2/articles_translated/art_*.json"
sentences_audio_dir = "course/sfid/phase4/output/sentences_audio"

sentence_ids = set()

for filepath in glob.glob(articles_path):
    with open(filepath, "r") as f:
        art = json.load(f)
    for s in art.get("sentences", []):
        sentence_ids.add(s.get("sentence_id"))

sentence_files = glob.glob(f"{sentences_audio_dir}/*.mp3")
extra_files = []

for sf in sentence_files:
    sid = os.path.basename(sf).replace(".mp3", "")
    if sid not in sentence_ids:
        extra_files.append(sid)

print("Extra sentence audio files:")
for e in extra_files:
    print(e)
