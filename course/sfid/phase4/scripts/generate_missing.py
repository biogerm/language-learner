import json, os, subprocess, shlex, time
import whisper
import Levenshtein
import warnings
warnings.filterwarnings("ignore")

VOICES = ["sv-SE-SofieNeural", "sv-SE-MattiasNeural"]

with open("output/missing_audio.json") as f:
    missing = json.load(f)

# Load original texts
target_texts = {}
import glob
for filepath in glob.glob("../phase2/articles/article_*.json"):
    with open(filepath) as f:
        article = json.load(f)
        if isinstance(article, dict):
            for item in article.get("sentences", []):
                target_texts[item["sentence_id"]] = item["sv"]

with open("../phase1/master_dictionary.json") as f:
    master = json.load(f)
    for base_form in master.get("words", {}).keys():
        target_texts[base_form] = base_form

with open("output/audio_manifest.json") as f:
    manifest = json.load(f)

print(f"Generating {len(missing['sentences'])} sentences and {len(missing['words'])} words...")
model = whisper.load_model("medium", download_root="../models")

def process_item(item_id, item_type, index):
    text = target_texts[item_id]
    voice = VOICES[index % 2]
    
    if item_type == "sentences":
        out_dir = "output/sentences_audio"
        filename = f"{item_id}.mp3"
    else:
        out_dir = "output/words_audio"
        filename = item_id.replace("/", "_") + ".mp3"
        
    mp3_path = os.path.join(out_dir, filename)
    safe_text = shlex.quote(text)
    cmd = f'python3 -m edge_tts --voice {voice} --rate=-20% --text {safe_text} --write-media "{mp3_path}"'
    
    success = False
    for attempt in range(5):
        try:
            subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if os.path.exists(mp3_path) and os.path.getsize(mp3_path) >= 1024:
                success = True
                break
        except Exception:
            pass
        time.sleep(1)
        
    if not success:
        return {"file": mp3_path.replace("output/", ""), "verification_score": 0.0, "status": "failed"}
        
    # Verify
    try:
        res = model.transcribe(mp3_path, language="sv")
        transcript = "".join([c for c in res["text"].lower().strip() if c.isalnum() or c.isspace()])
        target = "".join([c for c in text.lower().strip() if c.isalnum() or c.isspace()])
        
        if item_type == "words":
            similarity = 1.0 if target == transcript else 0.0
        else:
            distance = Levenshtein.distance(target, transcript)
            max_len = max(len(target), len(transcript))
            similarity = 1.0 - (distance / max_len) if max_len > 0 else 0.0
            
        status = "verified" if similarity >= 0.85 else "flagged"
        return {"file": mp3_path.replace("output/", ""), "verification_score": similarity, "status": status}
    except Exception:
        return {"file": mp3_path.replace("output/", ""), "verification_score": 0.0, "status": "failed"}

idx = 0
for s_id in missing["sentences"]:
    res = process_item(s_id, "sentences", idx)
    manifest["sentences"][s_id] = res
    idx += 1
    
for w_id in missing["words"]:
    res = process_item(w_id, "words", idx)
    manifest["words"][w_id] = res
    idx += 1

with open("output/audio_manifest.json", "w") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print("Done generating and verifying missing files!")
