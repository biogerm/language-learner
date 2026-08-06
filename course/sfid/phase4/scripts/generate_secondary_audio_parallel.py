import json, os, subprocess, shlex, time, glob
import whisper
import Levenshtein
import concurrent.futures
import warnings

warnings.filterwarnings("ignore")

VOICES = ["sv-SE-SofieNeural", "sv-SE-MattiasNeural"]

manifest_path = "course/sfid/phase4/output/audio_manifest.json"
with open(manifest_path) as f:
    manifest = json.load(f)

word_manifest = manifest.get("words", {})
word_audio_keys = set(word_manifest.keys())

missing_secondary = set()

for filepath in glob.glob("course/sfid/phase2/articles_translated/art_*.json"):
    with open(filepath, "r") as f:
        art = json.load(f)
    for s in art.get("sentences", []):
        for w in s.get("secondary_words", []):
            base_form = w.get("base_form")
            if base_form and base_form not in word_audio_keys:
                missing_secondary.add(base_form)

missing_secondary = list(missing_secondary)
print(f"Total secondary words missing audio: {len(missing_secondary)}")

if not missing_secondary:
    print("All secondary words already have audio.")
    exit(0)

# Global variables for the workers
global_model = None

def init_worker():
    global global_model
    import warnings
    warnings.filterwarnings("ignore")
    global_model = whisper.load_model("medium", download_root="course/sfid/phase4/models")

def process_item(args):
    text, index = args
    voice = VOICES[index % 2]
    out_dir = "course/sfid/phase4/output/words_audio"
    filename = text.replace("/", "_") + ".mp3"
    mp3_path = os.path.join(out_dir, filename)
    
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
        return text, {"file": mp3_path.replace("course/sfid/phase4/output/", ""), "verification_score": 0.0, "status": "failed"}
        
    try:
        res = global_model.transcribe(mp3_path, language="sv")
        transcript = "".join([c for c in res["text"].lower().strip() if c.isalnum() or c.isspace()])
        target = "".join([c for c in text.lower().strip() if c.isalnum() or c.isspace()])
        similarity = 1.0 if target == transcript else 0.0
        status = "verified" if similarity >= 0.85 else "flagged"
        return text, {"file": mp3_path.replace("course/sfid/phase4/output/", ""), "verification_score": similarity, "status": status}
    except Exception:
        return text, {"file": mp3_path.replace("course/sfid/phase4/output/", ""), "verification_score": 0.0, "status": "failed"}

if __name__ == '__main__':
    start_time = time.time()
    results_list = []
    
    tasks = [(w, i) for i, w in enumerate(missing_secondary)]
    
    # Process pool for CPU-bound whisper
    print("Spawning process pool for fast generation...")
    with concurrent.futures.ProcessPoolExecutor(max_workers=4, initializer=init_worker) as executor:
        for i, res in enumerate(executor.map(process_item, tasks)):
            results_list.append(res)
            if (i+1) % 50 == 0:
                print(f"Processed {i+1}/{len(missing_secondary)}...")
                
    # Save sequentially to manifest
    for w_id, res in results_list:
        manifest["words"][w_id] = res
        
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        
    print(f"\nDone! Total time: {time.time() - start_time:.2f} seconds.")

