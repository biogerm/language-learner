import json
import random
import whisper
import warnings

warnings.filterwarnings("ignore")

with open("../output/audio_manifest.json", "r") as f:
    manifest = json.load(f)

flagged = []
for k, v in manifest["sentences"].items():
    if v["status"] == "flagged":
        flagged.append((k, v["file"]))
for k, v in manifest["words"].items():
    if v["status"] == "flagged":
        flagged.append((k, v["file"]))

print(f"Total flagged: {len(flagged)}")
sample = random.sample(flagged, min(10, len(flagged)))

model = whisper.load_model("medium")
for k, file_path in sample:
    print(f"\nID: {k}")
    full_path = "../output/" + file_path
    res = model.transcribe(full_path, language="sv")
    print(f"Whisper heard: {res['text'].strip()}")
