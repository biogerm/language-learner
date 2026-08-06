import json, os, subprocess, shlex, time, glob
import whisper
import Levenshtein
import warnings
warnings.filterwarnings("ignore")

VOICES = ["sv-SE-SofieNeural", "sv-SE-MattiasNeural"]

# Load existing manifest
manifest_path = "course/sfid/phase4/output/audio_manifest.json"
with open(manifest_path) as f:
    manifest = json.load(f)

word_manifest = manifest.get("words", {})
word_audio_keys = set(word_manifest.keys())

missing_secondary = set()

# Gather missing secondary words
for filepath in glob.glob("course/sfid/phase2/articles_translated/art_*.json"):
    with open(filepath, "r") as f:
        art = json.load(f)
    for s in art.get("sentences", []):
        for w in s.get("secondary_words", []):
            base_form = w.get("base_form")
            if base_form and base_form not in word_audio_keys:
                missing_secondary.add(base_form)

missing_secondary = list(missing_secondary)
print(f"Found {len(missing_secondary)} secondary words missing audio.")

if len(missing_secondary) == 0:
    print("Nothing to do!")
    exit(0)

print("Loading Whisper model...")
model = whisper.load_model("medium", download_root="course/sfid/phase4/models")

out_dir = "course/sfid/phase4/output/words_audio"
os.makedirs(out_dir, exist_ok=True)

def process_item(text, index):
    voice = VOICES[index % 2]
    filename = text.replace("/", "_") + ".mp3"
    mp3_path = os.path.join(out_dir, filename)
    
    # We skip generation if file already exists and is valid (just in case it was interrupted)
    success = False
    if os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 1024:
        success = True
    else:
        safe_text = shlex.quote(text)
        cmd = f'python3 -m edge_tts --voice {voice} --rate=-20% --text {safe_text} --write-media "{mp3_path}"'
        
        for attempt in range(3):
            try:
                subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if os.path.exists(mp3_path) and os.path.getsize(mp3_path) >= 1024:
                    success = True
                    break
            except Exception:
                pass
            time.sleep(1)
            
    if not success:
        return {"file": mp3_path.replace("course/sfid/phase4/output/", ""), "verification_score": 0.0, "status": "failed"}
        
    # Verify with Whisper
    try:
        res = model.transcribe(mp3_path, language="sv")
        transcript = "".join([c for c in res["text"].lower().strip() if c.isalnum() or c.isspace()])
        target = "".join([c for c in text.lower().strip() if c.isalnum() or c.isspace()])
        
        # Word-level strict similarity check
        similarity = 1.0 if target == transcript else 0.0
        
        status = "verified" if similarity >= 0.85 else "flagged"
        return {"file": mp3_path.replace("course/sfid/phase4/output/", ""), "verification_score": similarity, "status": status}
    except Exception:
        return {"file": mp3_path.replace("course/sfid/phase4/output/", ""), "verification_score": 0.0, "status": "failed"}

# Since we don't want to wait 20 minutes blocking the chat, we will run this in background!
# But for now, we'll write the script, then launch it async.
print("Starting generation...")
batch_size = 50
for i, w_id in enumerate(missing_secondary):
    res = process_item(w_id, i)
    manifest["words"][w_id] = res
    
    # Periodically save manifest
    if (i + 1) % batch_size == 0 or (i + 1) == len(missing_secondary):
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        print(f"Processed {i+1}/{len(missing_secondary)}")

print("Done generating and verifying missing files!")
